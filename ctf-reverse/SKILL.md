---
name: ctf-reverse
description: Provides reverse engineering techniques for CTF challenges. Use when the main job is to understand how a compiled, obfuscated, packed, or virtualized target works before exploiting or solving it, including binaries, APKs, WASM, firmware, custom VMs, bytecode, game clients, malware-like loaders, and anti-debug or anti-analysis logic. Do not use it when the vulnerability is already understood and the remaining task is exploitation; use pwn instead. Do not use it for pure web workflows, log or disk forensics, or standalone crypto problems unless reversing the implementation is the real blocker.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Reverse Engineering

## Additional Resources

- [tools.md](references/tools.md) - Static analysis tools (GDB, Ghidra, radare2, IDA, Binary Ninja, dogbolt.org, Capstone, Unicorn, Python bytecode, WASM, APK, .NET, packed binaries)
- [tools-dynamic.md](references/tools-dynamic.md) - Dynamic analysis: Frida (hooking, anti-debug bypass, memory scanning), angr symbolic execution, lldb, x64dbg
- [tools-emulation.md](references/tools-emulation.md) - Emulation: Qiling (cross-platform OS-level), Triton (DSE), Intel Pin, LD_PRELOAD side-channel
- [tools-advanced.md](references/tools-advanced.md) - Advanced tools part 1: VMProtect/Themida analysis, binary diffing (BinDiff), deobfuscation frameworks (D-810, Miasm), Qiling, Rizin/Cutter, custom VM lifting to LLVM IR
- [tools-advanced-2.md](references/tools-advanced-2.md) - Advanced tools part 2: advanced GDB scripting, Ghidra scripting, binary patching (LIEF), GDB constraint extraction + ILP solver
- [anti-analysis.md](references/anti-analysis.md) - Anti-analysis taxonomy: Linux/Windows anti-debug, anti-VM/sandbox, anti-DBI (Frida detection), code integrity/self-hashing, anti-disassembly (opaque predicates), MBA identification, bypass strategies
- [anti-analysis-ctf.md](references/anti-analysis-ctf.md) - CTF writeup techniques: SIGILL/SIGFPE handler exploitation, instruction trace inversion, call-less function chaining, parent-patched child dump
- [patterns.md](references/patterns.md) - Foundational binary patterns: custom VMs, anti-debugging, nanomites, self-modifying code, XOR ciphers, LLVM obfuscation, SECCOMP/BPF, exception handlers, custom mangle reversing
- [patterns-runtime.md](references/patterns-runtime.md) - Runtime patching and oracle techniques: malware anti-analysis bypass, multi-stage shellcode, timing side-channel attacks, printf format string VM decompilation to Z3
- [patterns-ctf.md](references/patterns-ctf.md) - Competition patterns part 1: hidden emulator opcodes, LD_PRELOAD key extraction, GBA ROM meet-in-the-middle, custom binfmt kernel module, no-import ransomware
- [patterns-ctf-2.md](references/patterns-ctf-2.md) - Competition patterns part 2: multi-layer self-decrypting, lattice integer validation, decision tree obfuscation, GF(2^8) Gaussian elimination, ROPfuscation
- [patterns-ctf-3.md](references/patterns-ctf-3.md) - Competition patterns part 3: Z3 circuits, keyboard LED Morse, GLSL shader VM, TensorFlow DNN inversion, BPF filter analysis via kernel JIT
- [languages.md](references/languages.md) - Python bytecode & opcode remapping, Pyarmor, Unity IL2CPP, HarmonyOS HAP/ABC, Brainfuck/esolangs, UEFI, code coverage side-channel, FRACTRAN inversion
- [languages-platforms.md](references/languages-platforms.md) - Platform/framework: Roblox, Godot, Rust serde_json, Android JNI/DEX, Frida Firebase, Verilog/hardware RE, Electron ASAR, Node.js introspection
- [languages-compiled.md](references/languages-compiled.md) - Go (GoReSym, goroutines, embed.FS), Rust (demangling, Option/Result), Swift (protocol witness tables), Kotlin/JVM, Haskell GHC, C++ (vtable, RTTI)
- [platforms.md](references/platforms.md) - macOS/iOS (Mach-O, code signing, Objective-C/Swift runtime), embedded/IoT firmware (binwalk, UART/JTAG), kernel drivers (.ko, eBPF, .sys), game engines (Unreal, Unity, anti-cheat), automotive CAN bus
- [platforms-hardware.md](references/platforms-hardware.md) - Hardware RE: HD44780 LCD GPIO reconstruction, RISC-V (custom extensions, privileged modes), ARM64/AArch64 (calling convention, ROP, qemu-aarch64-static)
- [field-notes.md](references/field-notes.md) - Quick reference notes: binary types, anti-debugging bypass, specialized patterns, CTF case notes

## When to Pivot

- If you already understand the binary and now need heap, ROP, or kernel exploitation, switch to `/ctf-pwn`.
- If the challenge is really about recovering deleted files, PCAP data, or disk artifacts, switch to `/ctf-forensics`.
- If the target is a web app and you are only reversing a small client-side helper script, switch to `/ctf-web`.
- If the binary implements a machine learning model and the challenge is about model attacks or adversarial inputs, switch to `/ctf-ai-ml`.
- If the reversed binary's core logic is a cryptographic algorithm or math problem, switch to `/ctf-crypto`.
- If the binary is a real malware sample with C2, packing, or evasion behavior, switch to `/ctf-malware`.
- If the challenge is a toy VM, encoding puzzle, or pyjail rather than a real binary, switch to `/ctf-misc`.

## Problem-Solving Workflow

1. Try `strings` extraction -- many easy challenges have plaintext flags
2. Try `ltrace`/`strace` -- dynamic analysis often reveals flags without reversing
3. Try Frida hooking -- hook strcmp/memcmp to capture expected values
4. Try angr -- symbolic execution solves many flag-checkers automatically
5. Try Qiling -- emulate foreign-arch binaries or bypass heavy anti-debug
6. Map control flow before modifying execution
7. Automate manual processes via scripting (r2pipe, Frida, angr, Python)
8. Validate assumptions by comparing decompiler outputs (dogbolt.org for side-by-side)

## Quick Wins

```bash
# Plaintext flag extraction
strings binary | grep -E "flag\{|CTF\{|pico"
strings binary | grep -iE "flag|secret|password"
rabin2 -z binary | grep -i "flag"

# Dynamic analysis
ltrace ./binary
strace -f -s 500 ./binary

# Hex dump search
xxd binary | grep -i flag

# Run with test inputs
echo "test" | ./binary
./binary AAAA
```

## Initial Analysis

```bash
file binary           # Type, architecture
checksec --file=binary # Security features (for pwn)
chmod +x binary       # Make executable
```

## Comparison Direction

Two patterns: (1) `transform(flag) == stored_target` -- reverse the transform. (2) `transform(stored_target) == flag` -- flag IS the transformed data, just apply transform to stored target.

## Common Encryption Patterns

- XOR with single byte - try all 256 values
- XOR with known plaintext (`flag{`, `CTF{`)
- RC4 with hardcoded key
- Custom permutation + XOR
- XOR with position index (`^ i` or `^ (i & 0xff)`) layered with a repeating key

## Quick Tool Reference

```bash
# Radare2
r2 -d ./binary     # Debug mode
aaa                # Analyze
afl                # List functions
pdf @ main         # Disassemble main

# Ghidra (headless)
analyzeHeadless project/ tmp -import binary -postScript script.py
```
