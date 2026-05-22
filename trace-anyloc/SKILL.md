---
name: trace-anyloc
description: This skill should be used when setting up, adapting, or troubleshooting PangBaiWork/TraceAnyLoc (TAL) for Frida-based instruction tracing on 64-bit Linux, Windows, or Android targets, including binary control-flow analysis, VMP/obfuscation tracing, taint-string tracing, memory/register logging, and TraceAnyLoc test script customization.
---

# TraceAnyLoc

## Overview

Use TraceAnyLoc to instrument native 64-bit processes through Frida and load TAL's platform library (`libtal.so` or `tal.dll`) from a JavaScript agent. Configure the target module, trace offset, optional taint string, log path, and print mode before resuming the spawned process.

## Workflow

1. Identify the platform: Linux, Windows, or Android; TraceAnyLoc supports only 64-bit targets.
2. Install Frida Python dependencies with `pip install frida frida-tools` in the environment that runs the controller script.
3. Obtain the TAL runtime for the same platform and architecture: `linux/libtal.so`, `windows/tal.dll`, or `android/libtal.so` from the TraceAnyLoc release/repository.
4. Decide whether to spawn a local executable or attach to an already running target. Prefer spawn for repeatable CLI challenges because the script can load TAL before user input is consumed.
5. Determine the module name and trace address. Convert absolute runtime addresses to module-relative offsets with `traceOffset = absolute_address - module_base` when necessary.
6. Create or modify the Frida JavaScript agent to load TAL, resolve exports, set log path and taint string, then call `trace(mod.base.add(traceOffset), ptr(0), 1, PrintMode.TRACE)` or `PrintMode.TRACE_ARGS`.
7. Create or modify the Python runner to spawn the target, enable child gating, load the JS agent, resume only after the JS sends `script_ready`, and write stdin if needed.
8. Run from a directory where the configured log directory exists or can be created, then inspect generated TAL logs for register transitions, call symbols, memory reads/writes, and taint hits.

## Generate Templates

Use `scripts/make_traceanyloc_case.py` to generate a working pair of starter files for a new target:

```bash
python trace-anyloc/scripts/make_traceanyloc_case.py \
  --platform linux \
  --target ./Warning \
  --module Warning \
  --trace-offset 0x1120 \
  --tal-path ./linux/libtal.so \
  --input 'DASCTF{1111111111111111111111111111111111111111}\n' \
  --taint '1111111111111111111111111111111111111111' \
  --print-mode TRACE_ARGS \
  --out-dir ./tal_case
```

Edit the generated `trace_input.js` for advanced TAL controls such as `add_escape`, `add_resume`, alternate `trace` end addresses, or function argument printing policy. Edit `cli_trace.py` for non-stdin targets, delayed input, custom argv, custom environment variables, or Android device selection.

## Configuration Rules

Keep these TraceAnyLoc-specific rules in mind while adapting examples:

- Load TAL with `Module.load(talPath)` inside the Frida JS agent, not with `LD_PRELOAD`.
- Resolve exported functions with `tal.findExportByName(name)` and wrap them with `NativeFunction` before calling them.
- Set `target` to the module name visible to Frida, not necessarily the filesystem path used in Python argv.
- Set `traceOffset` as a module-relative offset. For PIE/ASLR targets, avoid hard-coded absolute addresses unless subtracting the runtime module base.
- Call `send("script_ready")` after TAL setup so the Python runner can safely resume the spawned process.
- Set `logPath` to a writable directory for the traced process context. Use package-private writable paths on Android.
- Match `taintStr` to the actual bytes that reach the program. Include or exclude newline deliberately depending on how input is consumed.
- Prefer `PrintMode.TRACE` for compact instruction/register/memory logs and `PrintMode.TRACE_ARGS` when function call arguments and demangled symbols matter.

## References

Read `references/traceanyloc-usage.md` when needing details about platform setup, exported TAL functions used by the public examples, address selection, log interpretation, Android notes, and common failure modes.

## Troubleshooting

- If `Process.getModuleByName(target)` fails, enumerate modules in Frida or adjust `target` to the loaded image name.
- If `Module.load(talPath)` fails, verify platform, architecture, absolute path, permissions, and dependent libraries.
- If no trace appears, verify the trace offset is reached, the target was resumed after `script_ready`, and the log path is writable.
- If trace exits too early around exceptions, signals, or anti-analysis control flow, add TAL escape/resume ranges in the JS agent.
- If stdin-dependent targets miss input, increase `time_to_input`, use manual input mode, or write input only after the expected prompt appears.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
