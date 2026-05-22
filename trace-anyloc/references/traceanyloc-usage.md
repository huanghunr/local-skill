# TraceAnyLoc Usage Reference

## Project Purpose

TraceAnyLoc (TAL) is a cross-platform high-performance arbitrary-address trace toolkit for 64-bit Windows, Linux, and Android targets. Use it for native binary control-flow analysis, VMP analysis, obfuscation analysis, taint-string tracking, function call argument logging, register monitoring before and after instruction execution, and memory read/write logging.

## Public Repository Layout

- `linux/libtal.so`: Linux TAL runtime library.
- `windows/tal.dll`: Windows TAL runtime library.
- `android/libtal.so`: Android TAL runtime library.
- `test/cli_trace_linux.py`: Frida Python local spawn example for Linux.
- `test/cli_trace_linux2.py`: Frida Python local spawn example for Linux with argv file input.
- `test/cli_trace_windows.py`: Frida Python local spawn example for Windows.
- `test/trace_input_linux.js`: Linux Frida JavaScript agent example.
- `test/trace_input_linux2.js`: Linux Frida JavaScript agent example for tracing `libark_jsruntime.so`.
- `test/trace_input_windows.js`: Windows Frida JavaScript agent example.
- `test/trace_input_android.js`: Android Frida JavaScript agent example.

## Frida Dependencies

Install both Python packages before using the public Python runners:

```bash
pip install frida frida-tools
```

Keep the `frida` Python package compatible with the target Frida server/gadget version, especially on Android.

## Core JavaScript Pattern

Use this pattern in `trace_input.js`:

```javascript
const target = "Warning";
const taintStr = "1111111111111111111111111111111111111111";
const traceOffset = 0x1120;
const logPath = "linux/";
const PrintMode = {ADDR: 0, BIN: 1, DEBUG: 2, TRACE: 3, TRITON: 4, TRACE_ARGS: 5};
const talPath = "/absolute/or/target-visible/path/to/libtal.so";

const cstr = Memory.allocUtf8String;
const mod = Process.getModuleByName(target);
const tal = Module.load(talPath);
const exp = (name, ret, args) => new NativeFunction(tal.findExportByName(name), ret, args);

const setLogPath = exp("set_log_path", "void", ["pointer"]);
const setTaintStr = exp("set_taint_str", "int", ["pointer"]);
const trace = exp("trace", "void", ["pointer", "pointer", "int", "int"]);
const addEscape = exp("add_escape", "void", ["pointer", "pointer"]);
const addResume = exp("add_resume", "void", ["pointer"]);
const setFunctionPrint = exp("set_function_print", "void", ["int", "int"]);

trace(mod.base.add(traceOffset), ptr(0), 1, PrintMode.TRACE_ARGS);
setLogPath(cstr(logPath));
setTaintStr(cstr(taintStr));
send("script_ready");
```

## Exported TAL Functions Seen In Examples

- `set_log_path(pointer) -> void`: Set trace output directory or file path root.
- `set_taint_str(pointer) -> int`: Set a string used by TAL taint tracking.
- `trace(pointer start, pointer end, int auto_context, int print_mode) -> void`: Start tracing at `start`; public examples pass `ptr(0)` as the end address and `1` for automatic context sync.
- `add_escape(pointer start, pointer end) -> void`: Mark an address range to escape or bypass when problematic control flow interrupts tracing.
- `add_resume(pointer addr) -> void`: Mark an address where tracing should resume.
- `set_function_print(int enabled, int argc_or_policy) -> void`: Configure function call printing policy when argument logging is needed.

## Print Modes

- `ADDR = 0`: Address-oriented output.
- `BIN = 1`: Binary-oriented output.
- `DEBUG = 2`: Debug output.
- `TRACE = 3`: Standard trace output with instruction, registers, and memory read/write records.
- `TRITON = 4`: Triton-related taint output.
- `TRACE_ARGS = 5`: Trace output plus function call arguments and demangled symbols where possible.

## Python Runner Pattern

Use the Python runner to spawn the target suspended, attach Frida, load the JS agent, and resume only after receiving `script_ready`. Preserve these elements from the public examples:

- `frida.get_local_device()` for Linux/Windows local tracing.
- `device.spawn(argv, env=env, stdio="pipe")` for repeatable CLI targets.
- `session.enable_child_gating()` to instrument child processes.
- `device.on("output", ...)` to mirror target stdout/stderr.
- `device.input(target=pid, data=input_str.encode())` to feed stdin after resume.
- `device.kill(pid)` on `KeyboardInterrupt` to avoid orphaned spawned processes.

For Android, prefer explicit device selection (`frida.get_usb_device()` or `frida.get_device(...)`) and ensure `libtal.so` plus logs live in paths readable/writable by the target process.

## Address Selection

Use module-relative offsets for `mod.base.add(traceOffset)`. When an analysis tool reports an absolute runtime address, calculate:

```text
traceOffset = absolute_runtime_address - runtime_module_base
```

For static ELF binaries, the TraceAnyLoc README notes that direct binary injection has special limitations. Use the author's `StaticElfLoader` project to load and run static ELF targets before analyzing them with TAL.

## Log Interpretation

Trace mode lines use this shape:

```text
module:offset: instruction  registers_before | registers_after | memory_reads_writes
```

Examples of useful markers:

- `call module:symbol`: Function call target resolved by TAL.
- `demangled : ...`: Demangled C++/native symbol when available.
- `argc` and `arg[n]`: Argument count and argument values in `TRACE_ARGS` mode.
- `R[address]=value <size>`: Memory read.
- `W[address]=value <size>`: Memory write.
- Quoted strings or hex dumps after pointer arguments: TAL-readable pointed-to memory.

## Common Adjustments

- Change `target` in JS when tracing a shared library loaded by an executable; keep Python `args[0]` as the executable path.
- Change `traceOffset` when moving from one build to another; offsets are build-specific.
- Change `taintStr` when the test input changes; mismatched taint strings make taint output misleading.
- Change `time_to_input` in Python for programs that initialize slowly or ask for input after a prompt.
- Use manual input mode (`time_to_input < 0`) when prompt timing varies.
- Create the log directory before running if the target process cannot create it.
