#!/usr/bin/env python3
"""Headless Binary Ninja obfuscation triage helper.

The script emits JSON metrics that help prioritize manual reverse engineering.
It is intentionally conservative and should be treated as a starting template,
not as an automatic deobfuscator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any, Iterable


if os.environ.get("BN_TRIAGE_ENABLE_PLUGINS") != "1":
    os.environ.setdefault("BN_DISABLE_USER_SETTINGS", "True")
    os.environ.setdefault("BN_DISABLE_USER_PLUGINS", "True")
    os.environ.setdefault("BN_DISABLE_REPOSITORY_PLUGINS", "True")

import binaryninja as bn  # noqa: E402


INDIRECT_OPS = {"LLIL_JUMP", "LLIL_JUMP_TO", "MLIL_JUMP", "MLIL_JUMP_TO"}
BRANCH_OPS = {"LLIL_IF", "MLIL_IF", "HLIL_IF"}
CONST_STORE_OPS = {"MLIL_STORE", "MLIL_SET_VAR"}


def hx(value: int | None) -> str | None:
    return None if value is None else hex(value)


def op_name(inst: Any) -> str:
    op = getattr(inst, "operation", None)
    return getattr(op, "name", str(op))


def short_text(obj: Any, limit: int = 180) -> str:
    text = str(obj).replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def iter_il_tree(expr: Any, seen: set[int] | None = None) -> Iterable[Any]:
    if seen is None:
        seen = set()
    if not hasattr(expr, "operands"):
        return
    ident = id(expr)
    if ident in seen:
        return
    seen.add(ident)
    for operand in getattr(expr, "operands", []) or []:
        if isinstance(operand, (list, tuple)):
            for item in operand:
                if hasattr(item, "operation"):
                    yield item
                    yield from iter_il_tree(item, seen)
        elif hasattr(operand, "operation"):
            yield operand
            yield from iter_il_tree(operand, seen)


def int_from_value(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    inner = getattr(value, "value", None)
    return inner if isinstance(inner, int) else None


def constants_in_expr(expr: Any) -> list[int]:
    out: list[int] = []
    for node in [expr, *iter_il_tree(expr)]:
        for attr in ("constant", "value"):
            value = int_from_value(getattr(node, attr, None))
            if value is not None:
                out.append(value)
    return out


def printable_score(value: int) -> int:
    if value < 0:
        return 0
    size = max(1, min(16, (value.bit_length() + 7) // 8))
    data = value.to_bytes(size, "little", signed=False).rstrip(b"\x00")
    return sum(1 for byte in data if 0x20 <= byte <= 0x7e)


def possible_values_text(expr: Any) -> str | None:
    try:
        return short_text(expr.possible_values)
    except Exception:
        return None


def collect_il_metrics(func: Any, il_name: str, limit_findings: int) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "operation_counts": {},
        "indirect_branches": [],
        "branch_candidates": [],
        "constant_store_candidates": [],
    }
    try:
        il = getattr(func, il_name)
    except Exception as exc:
        metrics["error"] = repr(exc)
        return metrics

    counts: Counter[str] = Counter()
    for block in il or []:
        for inst in block:
            name = op_name(inst)
            counts[name] += 1
            addr = getattr(inst, "address", None)

            if name in INDIRECT_OPS and len(metrics["indirect_branches"]) < limit_findings:
                metrics["indirect_branches"].append({
                    "address": hx(addr),
                    "operation": name,
                    "text": short_text(inst),
                })

            if name in BRANCH_OPS and len(metrics["branch_candidates"]) < limit_findings:
                cond = getattr(inst, "condition", None)
                metrics["branch_candidates"].append({
                    "address": hx(addr),
                    "operation": name,
                    "condition": short_text(cond) if cond is not None else None,
                    "possible_values": possible_values_text(cond) if cond is not None else None,
                })

            if name in CONST_STORE_OPS and len(metrics["constant_store_candidates"]) < limit_findings:
                constants = [c for c in constants_in_expr(inst) if printable_score(c) >= 3]
                if constants:
                    metrics["constant_store_candidates"].append({
                        "address": hx(addr),
                        "operation": name,
                        "constants": [hex(c) for c in constants[:8]],
                        "text": short_text(inst),
                    })

    metrics["operation_counts"] = dict(counts.most_common(40))
    return metrics


def collect_cfg_metrics(func: Any) -> dict[str, Any]:
    blocks = list(getattr(func, "basic_blocks", []) or [])
    fan_in: defaultdict[int, int] = defaultdict(int)
    edges: list[tuple[int, int, str]] = []

    for block in blocks:
        for edge in getattr(block, "outgoing_edges", []) or []:
            dst = edge.target.start
            fan_in[dst] += 1
            edges.append((block.start, dst, getattr(edge.type, "name", str(edge.type))))

    dispatcher_threshold = max(4, len(blocks) // 4) if blocks else 4
    dispatchers = [addr for addr, count in fan_in.items() if count >= dispatcher_threshold]

    return {
        "block_count": len(blocks),
        "edge_count": len(edges),
        "max_fan_in": max(fan_in.values()) if fan_in else 0,
        "dispatcher_threshold": dispatcher_threshold,
        "dispatcher_candidates": [hex(addr) for addr in sorted(dispatchers)[:16]],
        "edge_type_counts": dict(Counter(kind for _src, _dst, kind in edges)),
    }


def collect_function(func: Any, limit_findings: int) -> dict[str, Any]:
    entry = {
        "name": func.name,
        "start": hx(func.start),
        "total_bytes": getattr(func, "total_bytes", None),
        "call_site_count": len(getattr(func, "call_sites", []) or []),
        "caller_count": len(getattr(func, "callers", []) or []),
        "callee_count": len(getattr(func, "callees", []) or []),
        "cfg": collect_cfg_metrics(func),
        "llil": collect_il_metrics(func, "llil", limit_findings),
        "mlil": collect_il_metrics(func, "mlil", limit_findings),
    }
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage Binary Ninja obfuscation candidates")
    parser.add_argument("binary", help="Binary or BNDB to analyze")
    parser.add_argument("--top", type=int, default=30, help="number of largest functions to include")
    parser.add_argument("--limit-findings", type=int, default=20, help="max findings per category per function")
    parser.add_argument("--basic", action="store_true", help="use basic analysis mode")
    args = parser.parse_args()

    bn.disable_default_log()
    options = {"analysis.mode": "basic"} if args.basic else {}

    with bn.load(args.binary, options=options) as bv:
        functions = sorted(list(bv.functions), key=lambda f: getattr(f, "total_bytes", 0), reverse=True)
        selected = functions[: args.top]
        result = {
            "file": bv.file.filename,
            "arch": getattr(bv.arch, "name", str(bv.arch)),
            "entry_point": hx(getattr(bv, "entry_point", None)),
            "function_count": len(functions),
            "selected_function_count": len(selected),
            "functions": [collect_function(func, args.limit_findings) for func in selected],
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
