---
name: ctf-misc
description: Provides miscellaneous CTF challenge techniques for problems that do not cleanly fit the main categories. Use for encoding puzzles, pyjails, bash jails, RF/SDR, DNS oddities, unicode tricks, esoteric languages, QR or audio puzzles, constraint solving, game theory, unusual sandbox escapes, and hybrid logic puzzles. Prefer a more specific skill first when the challenge is mainly web, pwn, reverse, forensics, malware, OSINT, or crypto. Treat this as the fallback skill for genuine cross-category or edge-case challenges, not the default starting point.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch Skill
metadata:
  user-invocable: "false"
---

# CTF Miscellaneous

## Additional Resources

- [pyjails.md](references/pyjails.md) - Python jail/sandbox escape techniques, quine context detection, restricted character repunit decomposition, func_globals module chain traversal, f-string config injection via stored eval
- [bashjails.md](references/bashjails.md) - Bash jail/restricted shell escape techniques, HISTFILE file read trick, bash -v verbose mode, ctypes.sh direct C library calls
- [encodings.md](references/encodings.md) - Encodings, QR codes, esolangs, UTF-16 tricks, BCD encoding, multi-layer auto-decoding, indexed directory QR reassembly, multi-stage URL encoding chains
- [encodings-advanced.md](references/encodings-advanced.md) - Verilog/HDL, Gray code cyclic encoding, RTF custom tag extraction, SMS PDU decoding, multi-encoding sequential solvers, UTF-9, pixel binary encoding, hexadecimal Sudoku + QR assembly, TOPKEK, MaxiCode
- [rf-sdr.md](references/rf-sdr.md) - RF/SDR/IQ signal processing (QAM-16, carrier recovery, timing sync)
- [dns.md](references/dns.md) - DNS exploitation (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling)
- [games-and-vms.md](references/games-and-vms.md) - WASM patching, Roblox, PyInstaller, marshal analysis, Python env RCE, Z3 (including boolean logic gate network SAT solving), K8s RBAC, floating-point precision exploitation, custom assembly language sandbox escape
- [games-and-vms-2.md](references/games-and-vms-2.md) - Cookie checkpoint game brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, De Bruijn sequence, Brainfuck instrumentation, WASM linear memory manipulation
- [games-and-vms-3.md](references/games-and-vms-3.md) - memfd_create packed binaries, multi-phase crypto games with HMAC commitment-reveal and GF(256) Nim, emulator ROM-switching, BuildKit daemon exploitation, Docker container escape, Levenshtein distance oracle attack, taint analysis bypass, shredded document pixel-edge reassembly
- [games-and-vms-4.md](references/games-and-vms-4.md) - XSLT as Turing-complete VM, JavaScript MAX_SAFE_INTEGER equality, binary search oracle, blind SQLi via script-engine timeout, OEIS sequence lookup, QR reassembly from format-string constraints, Selenium + Tesseract CAPTCHA, Brainfuck-to-Piet polyglot
- [linux-privesc.md](references/linux-privesc.md) - Sudo wildcard parameter injection, monit confcheck injection, PostgreSQL COPY TO PROGRAM RCE, backup cronjob SUID, NFS share exploitation, SSH Unix socket tunneling, Squid proxy pivoting, Zabbix admin password reset, WinSSHTerm credential decryption
- [ctfd-navigation.md](references/ctfd-navigation.md) - CTFd platform API navigation without browser: detection, token auth, challenge listing, file download, flag submission, scoreboard, hints, notifications, Python client class

## When to Pivot

- If the puzzle is actually centered on cryptography or number theory, switch to `/ctf-crypto`.
- If the challenge is a real binary exploit instead of a jail, toy VM, or encoding problem, switch to `/ctf-pwn` or `/ctf-reverse`.
- If the input is mostly files, images, audio, or packet captures that need recovery work first, switch to `/ctf-forensics`.
- For ML/AI techniques (model attacks, adversarial examples, LLM jailbreaking), switch to `/ctf-ai-ml`.

## Quick Start Commands

```bash
# File identification
file mystery_file
xxd mystery_file | head -5

# Encoding detection / decoding
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR code
zbarimg qr.png

# Z3 constraint solving
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python jail test
python3 -c "__import__('os').system('id')"

# Find SUID binaries
find / -perm -4000 2>/dev/null

# GECOS field passwords
cat /etc/passwd  # Check 5th colon-separated field

# Docker group privilege escalation
id | grep -q docker && docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```

## Cipher Identification Workflow

1. **ROT13** - Challenge mentions "ROT", text looks like garbled English
2. **Base64** - `A-Za-z0-9+/=`, title hints "64"
3. **Base32** - `A-Z2-7=` uppercase only
4. **Atbash** - Title hints (Abash/Atbash), preserves spaces, 1:1 substitution
5. **Pigpen** - Geometric symbols on grid
6. **Keyboard Shift** - Text looks like adjacent keys pressed
7. **Substitution** - Frequency analysis applicable

Auto-identify: [dCode Cipher Identifier](https://www.dcode.fr/cipher-identifier)

## CTFd Platform Navigation

Detect CTFd (`curl -s "$CTF_URL/api/v1/" | head -5`) and interact via API. **Ask the user for their API token** (CTFd Settings > Access Tokens). See [ctfd-navigation.md](references/ctfd-navigation.md) for full workflow, Python client class, and troubleshooting.

```bash
export CTF_URL="https://ctf.example.com" CTF_TOKEN="ctfd_your_token_here"
curl -s -H "Authorization: Token $CTF_TOKEN" "$CTF_URL/api/v1/challenges" | jq -r '.data[] | "\(.id)\t\(.value)pts\t\(.category)\t\(.name)"'
curl -s -X POST -H "Authorization: Token $CTF_TOKEN" -H "Content-Type: application/json" "$CTF_URL/api/v1/challenges/attempt" -d "{\"challenge_id\": $CID, \"submission\": \"flag{...}\"}"
```
