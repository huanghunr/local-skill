# Binary Ninja Python API Cheatsheet

## Headless Loading

Install the API with Binary Ninja's bundled `install_api.py` before running standalone Python scripts. Use Commercial, Ultimate, Enterprise, or headless licensing for headless automation.

```python
import binaryninja as bn

with bn.load("/path/to/binary") as bv:
    print(bv.arch.name, hex(bv.entry_point), len(list(bv.functions)))
```

Useful loading options:

```python
with bn.load(path, update_analysis=False) as bv:
    bv.update_analysis_and_wait()

with bn.load(path, options={
    "loader.imageBase": 0x400000,
    "analysis.mode": "basic",
    "analysis.initialAnalysisHold": True,
}) as bv:
    pass
```

Batch-processing guardrails:

- Call `bn.disable_default_log()` to reduce headless log noise.
- Call `bn.set_worker_thread_count(2)` before loading files when launching several processes.
- Use Python multiprocessing only with `spawn` or `forkserver`, not default `fork`.
- Disable plugins and settings with environment variables before importing `binaryninja` when deterministic output matters.

## BinaryView APIs

Common properties:

```python
bv.file.filename
bv.arch
bv.platform
bv.entry_point
bv.entry_function
bv.functions
bv.sections
bv.segments
bv.strings
```

Function lookup:

```python
func = bv.get_function_at(addr)
funcs = bv.get_functions_at(addr)
funcs = bv.get_functions_containing(addr)
funcs = bv.get_functions_by_name("main")
```

Bytes, search, and references:

```python
data = bv.read(addr, length)
hit = bv.find_next_data(start, b"\x90" * 8)
code_refs = list(bv.get_code_refs(addr))
data_refs = list(bv.get_data_refs(addr))
```

Annotations and database changes:

```python
bv.set_comment_at(addr, "reason")
comment = bv.get_comment_at(addr)
bv.add_tag(addr, "Suspicious", "opaque predicate candidate")
```

Patching primitives for simple branch or junk-code cleanup:

```python
old = bv.read(addr, length)
bv.write(addr, new_bytes)
bv.convert_to_nop(addr)
bv.always_branch(addr)
bv.never_branch(addr)
bv.invert_branch(addr)
```

Prefer preserving `old` bytes in reports before writing. Verify patch APIs against the current architecture and BN version before bulk patching.

## Function APIs

Common properties:

```python
func.name
func.start
func.total_bytes
func.basic_blocks
func.call_sites
func.caller_sites
func.callers
func.callees
func.vars
func.parameter_vars
func.return_type
func.type
```

IL forms:

```python
llil = func.llil
llil_ssa = func.llil.ssa_form
mlil = func.mlil
mlil_ssa = func.mlil.ssa_form
hlil = func.hlil
hlil_ssa = func.hlil.ssa_form
```

Address-based lookup:

```python
llil_inst = func.get_llil_at(addr)
hlil_inst = llil_inst.hlil if llil_inst else None
```

Use these for comments and reports:

```python
func.add_tag("Obfuscation", "dispatcher candidate")
func.add_tag("OpaquePredicate", "condition resolves true", addr)
func.request_debug_report("hlil")
```

## BasicBlock And CFG APIs

Native function basic blocks expose layout and graph shape:

```python
for block in func.basic_blocks:
    print(hex(block.start), hex(block.end), block.length)
    for edge in block.outgoing_edges:
        print(edge.type, hex(edge.target.start))
```

Use CFG metrics for obfuscation triage:

```python
blocks = list(func.basic_blocks)
edges = [(bb.start, e.target.start, e.type.name) for bb in blocks for e in bb.outgoing_edges]
out_degree = {bb.start: len(bb.outgoing_edges) for bb in blocks}
fan_in = {}
for _src, dst, _kind in edges:
    fan_in[dst] = fan_in.get(dst, 0) + 1
```

Dispatcher candidates often have high fan-in, high out-degree, loop participation, nearby state-variable writes, or indirect jump/switch behavior.

## BNIL Traversal

Iterate by block for LLIL, MLIL, and HLIL:

```python
for il_block in func.mlil:
    for inst in il_block:
        print(hex(inst.address), inst.instr_index, inst.operation, inst)
```

Iterate top-level instructions:

```python
for inst in func.hlil.instructions:
    print(inst.address, inst.operation, inst)
```

Common instruction fields:

```python
inst.address
inst.instr_index
inst.expr_index
inst.operation
inst.operands
inst.size
```

Operation-specific fields commonly used in deobfuscation:

```python
inst.src
inst.dest
inst.left
inst.right
inst.condition
inst.true
inst.false
inst.params
inst.output
inst.value
inst.constant
```

Use defensive `hasattr` checks because fields vary by operation.

Visitor APIs are useful for tree-shaped IL, especially HLIL:

```python
def visitor(operand_name, inst, instr_type_name, parent):
    if hasattr(inst, "operation"):
        print(operand_name, instr_type_name, inst)

func.mlil.root.visit_all(visitor)
```

## Important Operation Enums

Import likely enums explicitly:

```python
from binaryninja.enums import (
    BranchType,
    LowLevelILOperation,
    MediumLevelILOperation,
    HighLevelILOperation,
    RegisterValueType,
    VariableSourceType,
)
```

LLIL operations useful for obfuscation:

```python
LLIL_SET_REG, LLIL_LOAD, LLIL_STORE, LLIL_PUSH, LLIL_POP
LLIL_JUMP, LLIL_JUMP_TO, LLIL_CALL, LLIL_RET, LLIL_IF, LLIL_GOTO
LLIL_CMP_E, LLIL_CMP_NE, LLIL_CMP_SLT, LLIL_CMP_ULT
LLIL_ADD, LLIL_SUB, LLIL_AND, LLIL_OR, LLIL_XOR
LLIL_LSL, LLIL_LSR, LLIL_ASR, LLIL_ROL, LLIL_ROR
LLIL_NOP, LLIL_TRAP, LLIL_UNDEF, LLIL_UNIMPL
```

MLIL operations useful for data-flow and deobfuscation:

```python
MLIL_SET_VAR, MLIL_VAR, MLIL_VAR_PHI, MLIL_MEM_PHI
MLIL_LOAD, MLIL_STORE, MLIL_ADDRESS_OF, MLIL_CONST, MLIL_CONST_PTR
MLIL_JUMP, MLIL_JUMP_TO, MLIL_CALL, MLIL_RET, MLIL_IF, MLIL_GOTO
MLIL_CMP_E, MLIL_CMP_NE, MLIL_CMP_SLT, MLIL_CMP_ULT
MLIL_ADD, MLIL_SUB, MLIL_AND, MLIL_OR, MLIL_XOR
MLIL_LSL, MLIL_LSR, MLIL_ASR, MLIL_ROL, MLIL_ROR
MLIL_SX, MLIL_ZX, MLIL_LOW_PART, MLIL_NOP
```

HLIL operations useful for final readability checks:

```python
HLIL_IF, HLIL_WHILE, HLIL_DO_WHILE, HLIL_FOR, HLIL_SWITCH, HLIL_CASE
HLIL_CALL, HLIL_RET, HLIL_ASSIGN, HLIL_VAR_INIT, HLIL_VAR
HLIL_CONST, HLIL_CONST_PTR, HLIL_DEREF, HLIL_ARRAY_INDEX
```

## SSA And Data Flow

Use MLIL SSA for value tracing and opaque predicate confidence:

```python
ssa = func.mlil.ssa_form
for var in ssa.ssa_vars:
    def_inst = ssa.get_ssa_var_definition(var)
    use_insts = ssa.get_ssa_var_uses(var)
```

For a variable instruction, distinguish the variable expression from the SSA variable:

```python
ssa_expr = expr.ssa_form
ssa_var = ssa_expr.src
definition = ssa_expr.function.get_ssa_var_definition(ssa_var)
uses = ssa_expr.function.get_ssa_var_uses(ssa_var)
```

Query possible values on MLIL/HLIL expressions:

```python
pv = inst.condition.possible_values
print(pv)
```

Use `possible_values` as evidence, not proof, unless corroborated by LLIL and the original bytes.

## Cross-IL Mappings

Mappings are approximate. Prefer plural mappings when explaining evidence:

```python
mlil_inst = hlil_inst.mlil
mlil_sources = hlil_inst.mlils
llil_inst = hlil_inst.llil
llil_sources = hlil_inst.llils
```

Use LLIL for closest mapping to actual machine instructions. Use HLIL only after confirming that simplification did not hide relevant low-level behavior.

## IL Modification APIs

Modify LLIL or MLIL in Workflow Activities. Avoid modifying SSA forms directly. Avoid Python HLIL modification.

For single expression replacement:

```python
new_expr = il_func.nop(location)
il_func.replace_expr(old_expr.expr_index, new_expr)
il_func.finalize()
il_func.generate_ssa_form()
```

For copy transformations:

```python
from binaryninja import MediumLevelILFunction, ILSourceLocation

old_func = context.mlil
new_func = MediumLevelILFunction(old_func.arch, low_level_il=context.llil)
new_func.prepare_to_copy_function(old_func)

for old_block in old_func.basic_blocks:
    new_func.prepare_to_copy_block(old_block)
    for idx in range(old_block.start, old_block.end):
        old_inst = old_func[idx]
        loc = ILSourceLocation.from_instruction(old_inst)
        new_func.set_current_address(old_inst.address, old_block.arch)
        new_func.append(old_inst.copy_to(new_func), loc)

new_func.finalize()
new_func.generate_ssa_form()
context.mlil = new_func
```

When changing control flow, use `get_label_for_source_instruction`, `mark_label`, and the same label object for related `goto` or `if` targets. Check the official Workflow and IL modification docs before complex CFG rewrites.

## Uncommon API Rule

For unusual features such as custom architectures, lifters, advanced type containers, render layers, debug reports, firmware views, projects, or UI actions, inspect the official API docs before writing code. Do not guess method names for uncommon APIs.
