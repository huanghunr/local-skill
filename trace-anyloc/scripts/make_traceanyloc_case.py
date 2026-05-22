#!/usr/bin/env python3
"""Generate starter TraceAnyLoc Frida runner files."""

from __future__ import annotations

import argparse
from pathlib import Path


PRINT_MODES = {"ADDR", "BIN", "DEBUG", "TRACE", "TRITON", "TRACE_ARGS"}


def js_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def py_string(value: str) -> str:
    return repr(value)


def build_js(args: argparse.Namespace) -> str:
    return f'''const target = "{js_string(args.module)}";
const taintStr = "{js_string(args.taint)}";
const traceOffset = {args.trace_offset};
const logPath = "{js_string(args.log_path)}";
const PrintMode = {{ADDR: 0, BIN: 1, DEBUG: 2, TRACE: 3, TRITON: 4, TRACE_ARGS: 5}};
const talPath = "{js_string(args.tal_path)}";

const cstr = Memory.allocUtf8String;
const mod = Process.getModuleByName(target);
const tal = Module.load(talPath);
const exp = (name, ret, fnArgs) => new NativeFunction(tal.findExportByName(name), ret, fnArgs);

const setLogPath = exp("set_log_path", "void", ["pointer"]);
const setTaintStr = exp("set_taint_str", "int", ["pointer"]);
const trace = exp("trace", "void", ["pointer", "pointer", "int", "int"]);
const addEscape = exp("add_escape", "void", ["pointer", "pointer"]);
const addResume = exp("add_resume", "void", ["pointer"]);
const setFunctionPrint = exp("set_function_print", "void", ["int", "int"]);

console.log("[+] target base:", mod.base);

trace(mod.base.add(traceOffset), ptr(0), 1, PrintMode.{args.print_mode});
setLogPath(cstr(logPath));
setTaintStr(cstr(taintStr));

send("script_ready");
'''


def build_py(args: argparse.Namespace) -> str:
    argv_items = [args.target, *args.argv]
    argv_literal = "[" + ", ".join(py_string(item) for item in argv_items) + "]"
    input_literal = py_string(args.input)
    return f'''#!/usr/bin/env python3
import os
import threading
import time

import frida
from frida_tools.application import Reactor


INPUT_STR = {input_literal}
SCRIPT_FILE = "trace_input.js"
ARGS = {argv_literal}
TIME_TO_INPUT = {args.time_to_input}


class Application:
    def __init__(self):
        self._stop_requested = threading.Event()
        self._reactor = Reactor(run_until_return=lambda reactor: self._stop_requested.wait())
        self._device = frida.get_local_device()
        self._sessions = set()
        self._pids = set()

        self._device.on("child-added", lambda child: self._reactor.schedule(lambda: self._on_child_added(child)))
        self._device.on("child-removed", lambda child: self._reactor.schedule(lambda: self._on_child_removed(child)))
        self._device.on("output", lambda pid, fd, data: self._reactor.schedule(lambda: self._on_output(pid, fd, data)))

    def run(self):
        self._reactor.schedule(lambda: self._start())
        self._reactor.run()

    def _start(self):
        env = {{
            "BADGER": "badger-badger-badger",
            "SNAKE": "mushroom-mushroom",
        }}
        print(f"spawn(argv={{ARGS}})")
        pid = self._device.spawn(ARGS, env=env, stdio="pipe")
        self._instrument(pid)

    def _stop_if_idle(self):
        if len(self._sessions) == 0:
            self._stop_requested.set()

    def _instrument(self, pid):
        self._pids.add(pid)
        print(f"attach(pid={{pid}})")
        session = self._device.attach(pid)
        session.on("detached", lambda reason: self._reactor.schedule(lambda: self._on_detached(pid, session, reason)))

        print("enable_child_gating()")
        session.enable_child_gating()

        with open(SCRIPT_FILE, "r", encoding="utf-8") as file:
            content = file.read()
        script = session.create_script(content)
        script.on("message", lambda message, data: self._reactor.schedule(lambda: self._on_message(pid, message)))

        print("load()")
        script.load()
        self._sessions.add(session)

    def write_input(self, pid):
        if not INPUT_STR:
            return
        if TIME_TO_INPUT >= 0:
            time.sleep(TIME_TO_INPUT)
        else:
            input("Enter to input")
        self._device.input(target=pid, data=INPUT_STR.encode())

    def _on_child_added(self, child):
        print(f"child_added: {{child}}")
        self._instrument(child.pid)

    def _on_child_removed(self, child):
        print(f"child_removed: {{child}}")

    def _on_output(self, pid, fd, data):
        print(data.decode(errors="ignore"), end="", flush=True)

    def _on_detached(self, pid, session, reason):
        print(f"detached: pid={{pid}}, reason={{reason!r}}")
        self._sessions.discard(session)
        self._reactor.schedule(self._stop_if_idle, delay=0.5)

    def _on_message(self, pid, message):
        if message.get("type") == "send" and message.get("payload") == "script_ready":
            print(f"resume(pid={{pid}})")
            self._device.resume(pid)
            threading.Thread(target=self.write_input, args=(pid,), daemon=True).start()
        else:
            print(f"message: pid={{pid}}, payload={{message}}")

    def kill_all(self):
        print("\\nCtrl+C, killing frida spawned processes...")
        for pid in list(self._pids):
            try:
                print(f"kill pid={{pid}}")
                self._device.kill(pid)
            except Exception as exc:
                print(f"kill pid={{pid}} failed: {{exc}}")
        os._exit(130)


app = Application()
thread = threading.Thread(target=app.run, daemon=True)
thread.start()

try:
    while thread.is_alive():
        thread.join(0.2)
except KeyboardInterrupt:
    app.kill_all()
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TraceAnyLoc Frida Python/JS starter files.")
    parser.add_argument("--platform", choices=["linux", "windows", "android"], required=True, help="Target platform label for the case.")
    parser.add_argument("--target", required=True, help="Executable path used by Frida spawn, for example ./Warning.")
    parser.add_argument("--module", required=True, help="Loaded module name used by Process.getModuleByName().")
    parser.add_argument("--trace-offset", required=True, help="Module-relative trace offset, for example 0x1120.")
    parser.add_argument("--tal-path", required=True, help="Path to libtal.so or tal.dll visible to the traced process.")
    parser.add_argument("--taint", default="", help="Taint string configured through set_taint_str().")
    parser.add_argument("--input", default="", help="Input string written to target stdin after resume; use shell quoting for newlines.")
    parser.add_argument("--argv", nargs="*", default=[], help="Extra argv values passed after target.")
    parser.add_argument("--log-path", default=None, help="Trace log path. Defaults to '<platform>/'.")
    parser.add_argument("--print-mode", choices=sorted(PRINT_MODES), default="TRACE", help="TraceAnyLoc print mode.")
    parser.add_argument("--time-to-input", type=float, default=0.0, help="Delay before stdin write. Use negative for manual prompt.")
    parser.add_argument("--out-dir", default=".", help="Directory for generated files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.log_path is None:
        args.log_path = f"{args.platform}/"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "trace_input.js").write_text(build_js(args), encoding="utf-8")
    runner = out_dir / "cli_trace.py"
    runner.write_text(build_py(args), encoding="utf-8")
    runner.chmod(0o755)
    print(f"Wrote {runner}")
    print(f"Wrote {out_dir / 'trace_input.js'}")


if __name__ == "__main__":
    main()
