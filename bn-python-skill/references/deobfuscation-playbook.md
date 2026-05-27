# Deobfuscation Playbook With Binary Ninja

## General Loop

Run each deobfuscation pass as a hypothesis test:

1. Collect structural evidence from functions, basic blocks, edges, IL operations, calls, strings, and references.
2. Locate candidate addresses or instruction indices.
3. Verify semantics at LLIL or MLIL SSA.
4. Emit comments, tags, JSON reports, or debug graphs.
5. Patch or rewrite only after preserving original bytes and listing expected effects.
6. Re-run analysis and compare CFG, IL, and decompiler output.

Prefer scripts that produce repeatable evidence over ad-hoc UI observations.

## Control Flow Flattening

Typical signals:

- One or a few dispatcher blocks with high incoming edge count.
- A state variable that is assigned constants before returning to the dispatcher.
- A loop where many original blocks end in a jump back to the dispatcher.
- A large `switch`, jump table, indirect branch, or chain of state comparisons.
- Many small blocks with one real side effect plus a state update.

Binary Ninja approach:

```python
blocks = list(func.basic_blocks)
edges = [(bb.start, e.target.start, e.type.name) for bb in blocks for e in bb.outgoing_edges]
fan_in = {}
for _src, dst, _kind in edges:
    fan_in[dst] = fan_in.get(dst, 0) + 1
dispatchers = [addr for addr, n in fan_in.items() if n >= max(4, len(blocks) // 4)]
```

Use MLIL SSA to identify the state variable. Search `MLIL_SET_VAR`, `MLIL_VAR_PHI`, `MLIL_CMP_*`, and `MLIL_IF` near dispatcher-related blocks. Trace assignments with `get_ssa_var_definition()` and `get_ssa_var_uses()`.

Reconstruction plan:

- Map each state constant to the block reached by the dispatcher.
- Map each block's final state assignment to the next block.
- Build a recovered edge list in JSON or DOT before changing the binary.
- Patch dispatcher checks or produce an external recovered CFG if patching would be risky.

## Opaque Predicates

Typical signals:

- Conditional branch whose condition has a constant or single-range `possible_values` result.
- Arithmetic identity such as `(x * (x - 1)) & 1 == 0`, `(x ^ x) == 0`, or branch on masked constant bits.
- Predicate that dominates a dead or junk block and is repeated across many functions.
- Condition using complex arithmetic but no meaningful data dependency on user input.

Binary Ninja approach:

```python
for block in func.mlil:
    for inst in block:
        if inst.operation.name == "MLIL_IF":
            cond = inst.condition
            print(hex(inst.address), cond, getattr(cond, "possible_values", None))
```

Verification steps:

- Check MLIL SSA definitions of every variable used by the condition.
- Confirm the same constant truth value at LLIL and assembly.
- Confirm the discarded branch has no required side effects, calls, volatile memory operations, or exception behavior.
- Preserve original bytes before using `always_branch`, `never_branch`, or NOP patching.

## Junk Code And Dead Blocks

Typical signals:

- Blocks unreachable from the entry under a proven branch result.
- Long arithmetic chains that define variables with no uses.
- NOP-equivalent instructions such as `xor reg, 0`, `add reg, 0`, `mov reg, reg`, or paired inverse operations.
- Traps, invalid instructions, or impossible control flow on dead paths.

Binary Ninja approach:

- Use CFG reachability from `func.basic_blocks` and branch decisions from MLIL SSA.
- Use `get_ssa_var_uses()` to test whether computed values are used after a candidate junk sequence.
- Use LLIL operations to avoid missing flag side effects from assembly-looking no-ops.

Patch plan:

- Prefer replacing a whole proven-dead conditional with forced branch behavior.
- Avoid NOPing individual instructions until checking flags, memory writes, calls, and exception behavior.
- Re-run `bv.update_analysis_and_wait()` and compare block count and HLIL readability.

## Stack Strings And Constant Decoders

Typical signals:

- Many constant stores to stack or local buffers.
- Printable byte patterns in little-endian constants.
- Tight loops over a buffer using XOR, ADD, SUB, ROL, ROR, or table lookups.
- Calls to string or crypto-like routines immediately after buffer construction.

Binary Ninja approach:

```python
interesting = {"MLIL_STORE", "MLIL_SET_VAR"}
for block in func.mlil:
    for inst in block:
        if inst.operation.name in interesting:
            print(hex(inst.address), inst)
```

Use a recursive operand walker to extract constants from MLIL expressions. Convert constants to little-endian bytes and score printable runs. Use SSA to group stores targeting the same stack variable or pointer base.

Decode plan:

- Extract constant bytes in store order.
- Emulate only the small decode loop if operations are simple.
- Add decoded strings as comments at the constructor and xrefs to consumers.
- Avoid writing decoded bytes into the binary unless the task explicitly requires a patched artifact.

## Indirect Branches And Jump Tables

Typical signals:

- `LLIL_JUMP`, `LLIL_JUMP_TO`, `MLIL_JUMP`, or `MLIL_JUMP_TO` in non-compiler-looking locations.
- Branch target derived from arithmetic on a state variable or table lookup.
- Many code pointers in a data section or near dispatcher logic.

Binary Ninja approach:

```python
for block in func.llil:
    for inst in block:
        if inst.operation.name in {"LLIL_JUMP", "LLIL_JUMP_TO"}:
            print(hex(inst.address), inst)
```

Resolution steps:

- Query `possible_values` on the MLIL destination expression when available.
- Locate table memory with `bv.read()` and references with `bv.get_data_refs()` or `bv.get_code_refs()`.
- Verify candidate targets are valid code starts or inside known functions.
- Add recovered edges to an external report before patching.

## Call Graph And API Deobfuscation

Typical signals:

- Indirect calls through hash-resolved imports.
- Thin wrapper functions with high caller count and low byte count.
- Repeated decode or dispatch routines invoked before meaningful work.

Binary Ninja approach:

```python
for site in func.call_sites:
    print(hex(site.address), site.hlil)

for ref in target_func.caller_sites:
    print(hex(ref.address), ref.function.name, ref.hlil)
```

Use HLIL for call readability, then validate call destination and parameters in MLIL. Rename functions only after enough evidence, and keep generated names descriptive, such as `decode_stack_string`, `resolve_api_by_hash`, or `flatten_dispatcher`.

## Workflow IL Rewriting

Use Workflow IL rewriting to improve analysis, not as the first tool for executable patching.

Safe choices:

- Modify LLIL before MLIL generation when register semantics or stack analysis must change.
- Modify MLIL after MLIL generation when variables and possible values are needed.
- Do not modify SSA directly.
- Do not use Python to modify HLIL.

Minimum MLIL copy transformation shape:

```python
def rewrite_action(context):
    old_func = context.mlil
    new_func = MediumLevelILFunction(old_func.arch, low_level_il=context.llil)
    new_func.prepare_to_copy_function(old_func)

    for old_block in old_func.basic_blocks:
        new_func.prepare_to_copy_block(old_block)
        for idx in range(old_block.start, old_block.end):
            old_inst = old_func[idx]
            loc = ILSourceLocation.from_instruction(old_inst)
            new_func.set_current_address(old_inst.address, old_block.arch)
            if should_replace(old_inst):
                new_func.append(new_func.nop(loc), loc)
            else:
                new_func.append(old_inst.copy_to(new_func), loc)

    new_func.finalize()
    new_func.generate_ssa_form()
    context.mlil = new_func
```

Debugging rules:

- Add a dry-run mode that reports candidates without assigning `context.mlil`.
- Use custom debug reports for before and after graphs when rewriting CFG.
- Catch exceptions and show partial reports rather than silently breaking analysis.
- Re-run on small functions before applying to the whole binary.

## Reporting Format

For each candidate, emit fields similar to:

```json
{
  "function": "sub_401000",
  "address": "0x401234",
  "kind": "opaque_predicate",
  "confidence": "medium",
  "evidence": ["MLIL_IF condition possible_values is <const 0x1>", "false branch has no calls"],
  "suggested_action": "force always branch after preserving original bytes",
  "verification": ["check LLIL flag expression", "re-run analysis", "compare recovered CFG"]
}
```

Prefer conservative confidence. Mark anything involving memory aliasing, indirect calls, exception behavior, self-modifying code, or missing semantics as low confidence until dynamically verified.
