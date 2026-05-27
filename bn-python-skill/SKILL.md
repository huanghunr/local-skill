---
name: bn-python-skill
description: This skill should be used when automating reverse engineering with the Binary Ninja Python API for native binaries, especially obfuscation triage, control flow analysis, BNIL inspection, deobfuscation experiments, basic block and function analysis, patch planning, and workflow based IL rewriting.
---

# Binary Ninja Python Automation

## Purpose

Use Binary Ninja as a programmable analysis engine for native reverse engineering. Focus on repeatable scripts that inspect assembly, basic blocks, functions, call graphs, BNIL, SSA data flow, and deobfuscation candidates before making irreversible patches.

Use this skill for obfuscated binaries, CTF reverse engineering, malware-like unpacking stubs, custom VMs, flattened control flow, opaque predicates, stack strings, dead code, junk instruction patterns, indirect branches, and automated annotation or patch planning.

## Operating Modes

Prefer headless scripts for repeatable analysis. Use `binaryninja.load(path)` as a context manager, call `bv.update_analysis_and_wait()` when loading with delayed analysis, and close manually with `bv.file.close()` only when not using `with`.

Disable user settings or plugins before importing `binaryninja` when reproducibility matters:

```python
import os
os.environ["BN_DISABLE_USER_SETTINGS"] = "True"
os.environ["BN_DISABLE_USER_PLUGINS"] = "True"
os.environ["BN_DISABLE_REPOSITORY_PLUGINS"] = "True"
import binaryninja as bn
```

Use UI magic variables only inside Binary Ninja's Python console. Avoid `bv`, `current_function`, `current_il_instruction`, and `current_il_expr` in standalone scripts unless they are explicitly provided by the UI environment.

## Analysis Workflow

Start with non-destructive reconnaissance. Enumerate functions, blocks, edges, calls, strings, references, and suspicious IL operations. Annotate addresses, tags, and comments before patching bytes.

Choose the lowest abstraction level that preserves the signal:

- Use disassembly and `Function.basic_blocks` for layout, instruction bytes, branch density, block splitting, and patch locations.
- Use LLIL for register-level semantics, exact branch instructions, indirect jumps, flag-derived conditions, stack-pointer effects, and architecture-close transformations.
- Use MLIL or MLIL SSA for variables, constants, propagated values, `possible_values`, call parameters, memory loads and stores, opaque predicate checks, and data-flow tracing.
- Use HLIL for source-like queries and final readability checks, but avoid using HLIL as the only evidence for low-level patch decisions.

Treat IL address mappings as approximate. Prefer instruction indices and cross-IL mapping lists such as `hlil_inst.mlils` or `hlil_inst.llils` when precision matters.

## Deobfuscation Strategy

Classify the obfuscation before rewriting anything:

- Detect CFG flattening by finding dispatcher-like blocks with high fan-in, loops around a state variable, dense switch or indirect jump usage, and repeated writes to one state variable.
- Detect opaque predicates by querying MLIL SSA conditions and `possible_values`, then verify the backing LLIL and bytes before forcing branches.
- Detect junk code by finding unreachable blocks, side-effect-free arithmetic, repeated NOP-like operations, impossible branches, and values never used outside dead paths.
- Detect stack strings and constant decoding by locating repeated stores of printable constants, XOR/add/sub/rol/ror loops, short decode loops, and references to newly decoded buffers.
- Detect indirect branch obfuscation by collecting `LLIL_JUMP`, `LLIL_JUMP_TO`, `MLIL_JUMP`, and `MLIL_JUMP_TO`, then resolving targets from constants, tables, or value sets.

Prefer a staged output: evidence, candidate addresses, confidence, suggested action, and verification steps. Only patch when the semantic consequence is clear and reversible.

## Rewriting And Patching

Prefer annotation, database comments, and generated reports for uncertain findings. Patch only after proving the change at LLIL or MLIL and preserving original bytes.

Use byte patching for simple cases such as NOPing junk instructions or forcing a resolved branch. Use Workflow IL rewriting only when the goal is to improve Binary Ninja analysis or decompiler output rather than create a modified executable.

For IL modification, follow Binary Ninja's Workflow model. Modify LLIL or MLIL in Python; do not modify SSA forms directly; do not rely on Python HLIL modification because it is not supported. After `replace_expr` or copy transformations, call `finalize()` and `generate_ssa_form()` and assign the result back to `AnalysisContext`.

## Bundled References

Load `references/binary-ninja-api-cheatsheet.md` when writing or reviewing Binary Ninja automation code. It lists common APIs, operation enums, traversal patterns, data-flow APIs, and patching primitives.

Load `references/deobfuscation-playbook.md` when analyzing obfuscation or planning deobfuscation. It provides practical heuristics, evidence checks, and API patterns for flattening, opaque predicates, stack strings, indirect branches, dead code, and workflow rewriting.

Use `scripts/bn_obfuscation_triage.py` as a starting point for headless triage. Run it on a binary to produce JSON metrics for functions, CFG shape, IL operation counts, indirect branches, opaque predicate candidates, and constant-store patterns.

## Documentation Policy

Use only the likely APIs documented in this skill for first-pass scripts. When a task needs an uncommon Binary Ninja API, inspect the official documentation first at `https://api.binary.ninja/index.html` or `https://docs.binary.ninja/dev/`, then cite the API assumptions in the script comments or final notes.
