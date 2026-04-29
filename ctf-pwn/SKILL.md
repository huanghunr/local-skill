---
name: ctf-pwn
description: Provides binary exploitation techniques for CTF challenges. Use when you already have a vulnerable native target or service and need to turn memory corruption or low-level primitives into code execution or privilege escalation, such as buffer overflows, format strings, heap bugs, ROP, ret2libc, shellcode, kernel exploitation, seccomp bypass, sandbox escape, or Windows/Linux exploit chains. Do not use it when the main blocker is understanding what the binary does; use reverse engineering first. Do not use it for pure web bugs, disk or packet forensics, or standalone crypto/math challenges.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Binary Exploitation (Pwn)

## Additional Resources

- [overflow-basics.md](references/overflow-basics.md) - Stack/global buffer overflow, ret2win, canary bypass, canary byte-by-byte brute force on forking servers, struct pointer overwrite, signed integer bypass, hidden gadgets
- [rop-and-shellcode.md](references/rop-and-shellcode.md) - Core ROP chains (ret2libc, syscall ROP, rdx control), ret2csu, bad character XOR bypass, exotic x86 gadgets, stack pivot, canary XOR epilogue, stub_execveat syscall
- [rop-advanced.md](references/rop-advanced.md) - Advanced ROP: double stack pivot, SROP, seccomp bypass, RETF architecture switch (x64->x32), .fini_array hijack, ret2vdso, x32 ABI syscall aliasing
- [format-string.md](references/format-string.md) - Format string exploitation (leaks, GOT overwrite, blind pwn, filter bypass, .fini_array loop, __printf_chk bypass)
- [advanced.md](references/advanced.md) - Seccomp advanced, UAF, JIT, esoteric GOT, heap overlap, ret2dlresolve, kernel exploitation basics
- [heap-techniques.md](references/heap-techniques.md) - House of Apple 2, House of Einherjar/Orange/Spirit/Lore/Force, heap grooming, custom allocators, tcache stashing unlink attack, musl libc heap
- [heap-techniques-2.md](references/heap-techniques-2.md) - CTF-writeup heap variants: UAF vtable pointer encoding, tcache poisoning, IS_MMAPED bit-flip, custom allocator unsafe unlink
- [heap-fsop.md](references/heap-fsop.md) - _IO_FILE exploitation: fastbin stdout vtable hijack, _IO_buf_base stdin hijack, unsorted-bin attack, realloc UAF
- [advanced-exploits.md](references/advanced-exploits.md) - Advanced techniques part 1: VM signed comparison, BF JIT shellcode, type confusion, DNS overflow, MD5 preimage gadgets
- [advanced-exploits-2.md](references/advanced-exploits-2.md) - Advanced techniques part 2: bytecode validator bypass, io_uring UAF, GC null-reference corruption, XSS-to-binary pwn bridge
- [advanced-exploits-3.md](references/advanced-exploits-3.md) - Advanced techniques part 3: JIT sandbox escape, DNS compression pointer ROP, CRC oracle as arbitrary read, UTF-8 case conversion overflow
- [advanced-exploits-4.md](references/advanced-exploits-4.md) - Advanced techniques part 4: Windows SEH overwrite, ARM Thumb shellcode, GF(2) Gaussian elimination tcache poisoning, neural network OOB
- [advanced-exploits-5.md](references/advanced-exploits-5.md) - Advanced techniques part 5: data-interpretation exploitation (Chip-8 OOB, float quicksort canary repositioning, bloom filter OOB)
- [sandbox-escape.md](references/sandbox-escape.md) - Custom VM exploitation, FUSE/CUSE devices, restricted shell, process_vm_readv bypass, CPU emulator eval injection
- [kernel.md](references/kernel.md) - Linux kernel exploitation: environment setup, QEMU debug, heap spray structures, kernel stack overflow, privilege escalation (ret2usr, kernel ROP)
- [kernel-techniques.md](references/kernel-techniques.md) - Kernel techniques: tty_struct kROP, AAW via ioctl, userfaultfd race, SLUB allocator internals, addr_limit bypass, cross-cache CPU-split attack
- [kernel-bypass.md](references/kernel-bypass.md) - Kernel protection bypass: KASLR/FGKASLR, KPTI, SMEP/SMAP, GDB kernel module debugging, initramfs/virtio-9p workflow
- [field-notes.md](references/field-notes.md) - Detailed pwn notes: heap exploitation quick reference, useful commands

## When to Pivot

- If you do not yet understand what the binary does, switch to `/ctf-reverse` before trying to exploit it.
- If the service is really a restricted shell, encoding puzzle, or sandbox language challenge, switch to `/ctf-misc`.
- If the exploit path depends on a web endpoint, session bug, or upload primitive more than memory corruption, switch to `/ctf-web`.
- If the vulnerability requires breaking a cryptographic primitive before exploitation, switch to `/ctf-crypto`.

## Quick Start Commands

```bash
# Binary analysis
checksec --file=binary
file binary
readelf -h binary

# Find gadgets
ROPgadget --binary binary | grep "pop rdi"
ropper -f binary --search "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6

# Debug
gdb -q binary -ex 'start' -ex 'checksec'

# Pattern for offset finding
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616168))"

# libc identification
./libc-database/find puts <leaked_addr_last_3_nibbles>
```

## Protection Implications for Exploit Strategy

| Protection | Status | Implication |
|-----------|--------|-------------|
| PIE | Disabled | All addresses (GOT, PLT, functions) are fixed - direct overwrites work |
| RELRO | Partial | GOT is writable - GOT overwrite attacks possible |
| RELRO | Full | GOT is read-only - need alternative targets (hooks, vtables, return addr) |
| NX | Enabled | Can't execute shellcode on stack/heap - use ROP or ret2win |
| Canary | Present | Stack smash detected - need leak or avoid stack overflow (use heap) |

**Quick decision tree:**
- Partial RELRO + No PIE -> GOT overwrite (easiest, use fixed addresses)
- Full RELRO -> target `__free_hook`, `__malloc_hook` (glibc < 2.34), or return addresses
- Stack canary present -> prefer heap-based attacks or leak canary first

## Stack Buffer Overflow

1. Find offset: `cyclic 200` then `cyclic -l <value>`
2. Check protections: `checksec --file=binary`
3. No PIE + No canary = direct ROP
4. Canary leak via format string or partial overwrite
5. Canary brute-force byte-by-byte on forking servers (7*256 attempts max)

## Source Code Red Flags

- Threading/`pthread` -> race conditions
- `usleep()`/`sleep()` -> timing windows
- Global variables in multiple threads -> TOCTOU

## Common Vulnerabilities

- Buffer overflow: `gets()`, `scanf("%s")`, `strcpy()`
- Format string: `printf(user_input)`
- Integer overflow, UAF, race conditions
