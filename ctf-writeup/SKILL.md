---
name: ctf-writeup
description: Generates a single standardized submission-style CTF writeup for competition handoff and organizer review. Use after solving a CTF challenge to document the solution steps, tools used, and lessons learned in a structured format.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash and Python 3.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "true"
  argument-hint: "[challenge-name]"
---

# CTF Write-up Generator

Generate a standardized submission-style CTF writeup for a solved challenge.

Default behavior:
- During an active competition, optimize for speed, clarity, and reproducibility
- Keep writeups short enough that a teammate or organizer can validate the solve quickly
- Always produce a `submission`-style writeup
- Prefer one complete solve script from challenge data to final flag

## Workflow

### Step 1: Gather Information

Collect challenge metadata (name, CTF event, category, difficulty, points, flag format) and solution artifacts (exploit scripts, payloads, command output).

```bash
# Scan for exploit scripts and artifacts
find . -name '*.py' -o -name '*.sh' -o -name 'exploit*' -o -name 'solve*' | head -20
# Check for flags in output files
grep -rniE '(flag|ctf|eno|htb|pico)\{' . 2>/dev/null
```

### Step 2: Generate Write-up

Write the writeup file as `writeup.md` (or `writeup-<challenge-name>.md`) using the template below.

## Template

```markdown
---
title: "<Challenge Name>"
ctf: "<CTF Event Name>"
date: YYYY-MM-DD
category: web|pwn|crypto|reverse|forensics|osint|malware|misc
difficulty: easy|medium|hard
points: <number>
flag_format: "flag{...}"
author: "<your name or team>"
---

# <Challenge Name>

## Summary
<1-2 sentences: what the challenge was and the core technique.>

## Solution

### Step 1: <Action>
<Explain the key observation in 3-8 short lines.>

```python
<one complete solving script from provided challenge data to printing the final flag>
```

### Step 2: <Action> (optional)
<Only add when a second short step genuinely helps readability.>

### Step 3: <Action> (optional)
<Use only if the challenge really needs it. Keep the total number of steps small.>

## Flag
```
flag{example_flag_here}
```
```

## Guidance

- Prefer 1-3 short steps total
- Keep code to the smallest complete solving script
- Do not split "recover secret", "derive key", and "decrypt flag" into separate partial snippets
- The script should start from the challenge data and end by printing the flag
- Avoid long background sections, dead ends, or multiple alternative solves
- Redact the flag only if the user explicitly asks for redaction
- Tag code blocks with language (`python`, `bash`, `sql`, etc.)
- Include all imports and correct variable names

## Challenge

$ARGUMENTS
