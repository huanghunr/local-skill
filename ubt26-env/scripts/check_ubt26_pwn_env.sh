#!/usr/bin/env bash
set -euo pipefail

export PATH="/home/nixos/ubt26-home/.local/bin:/home/nixos/ubt26-home/.local/share/gem/ruby/3.3.0/bin:$PATH"
export PWNDBG_NO_AUTOUPDATE=1

printf 'container='; . /etc/os-release && printf '%s %s\n' "$ID" "$VERSION_ID"
printf 'user='; whoami

for tool in gcc gdb pwn ROPgadget ropper pwninit one_gadget seccomp-tools checksec patchelf qemu-x86_64; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%-14s %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%-14s missing\n' "$tool"
  fi
done

printf 'LIBC_DATABASE=%s\n' "${LIBC_DATABASE:-/home/nixos/ubt26-home/.local/src/libc-database}"
printf 'LIBC_ALL_IN_ONE=%s\n' "${LIBC_ALL_IN_ONE:-/home/nixos/ubt26-home/.local/src/libc-all-in-one}"
HOME=/home/nixos/ubt26-home gdb -q -ex 'pi print("pwndbg-ok")' -ex quit
