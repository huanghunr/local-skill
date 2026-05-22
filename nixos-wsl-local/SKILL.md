---
name: nixos-wsl-local
description: |
  This skill provides knowledge about this specific NixOS-on-WSL machine for system operations.
  Use when the user asks about installing packages, searching nixpkgs, rebuilding the WSL NixOS
  system, managing generations, using nix-shell or nix develop, debugging Nix build failures,
  navigating the local flake configuration, using WSL integration, USB/IP, containers, or
  understanding environment-specific tool usage on this machine.
  This skill should be used for any task involving Nix package management, NixOS administration,
  WSL-specific behavior, or local development/security tooling on this machine.
---

# NixOS WSL Local Machine Reference

## Overview

This skill covers the local NixOS 25.11 (Xantusia) system running inside WSL2. The system is managed via the flake at `/etc/nixos/flake.nix`, backed by the git tree `/home/nixos/nixos-config`, with Home Manager integrated for the `nixos` user. The default interactive shell is fish via a wrapped bash login shell, and the environment is optimized for development, security research, reverse engineering, CTF tooling, containers, and MCP/agent workflows.

## Quick Reference

- **System flake**: `/etc/nixos/flake.nix`
- **Flake backing git tree**: `/home/nixos/nixos-config`
- **System config**: `/etc/nixos/configuration.nix`
- **NixOS module entry**: `/etc/nixos/nixos/default.nix`
- **Home config**: `/etc/nixos/home/home.nix`
- **Rebuild command**: `sudo nixos-rebuild switch --flake /etc/nixos#nixos`
- **User**: `nixos`
- **Arch**: `x86_64-linux`
- **Platform**: WSL2, kernel `6.6.87.2-microsoft-standard-WSL2`
- **Windows mount**: `/mnt/c`

When hardware, installed tools, services, or WSL-specific details are needed, read `references/system_info.md`.

## Package Operations

### Searching for Packages

Use the `mcp-nixos_nix` tool for up-to-date package and option search results. Prefer it over `nix search` because it returns current indexed channel data.

Command-line fallback:

```bash
nix search nixpkgs <keyword>
nix search nixpkgs#<pkgname>
```

### Trying a Package Temporarily

```bash
nix-shell -p <pkgname>
nix-shell -p <pkg1> <pkg2> <pkg3>
nix shell nixpkgs/nixos-unstable#<pkgname>
nix-shell shell.nix
nix develop
```

For complex temporary environments, create a `shell.nix` with `pkgs.mkShell` or a project `flake.nix` with `devShells`. See `references/nix_tips.md` for examples.

### Getting the Latest Version

This system has an `unstablepkgs` input (`nixos-unstable`) imported as `upkgs` in `/etc/nixos/flake.nix`.

- **Try in shell**: `nix shell nixpkgs/nixos-unstable#<pkgname>`
- **Add to config**: use `upkgs.<name>` in modules that receive `upkgs`
- **Caveat**: mixing stable and unstable packages can cause dependency conflicts

### Adding a Package Permanently

System-wide packages go in `/etc/nixos/configuration.nix` under `environment.systemPackages` or in a module imported by `/etc/nixos/nixos/default.nix`.

User packages go in `/etc/nixos/home/home.nix` or one of the imported Home Manager modules under `/etc/nixos/home/modules/`.

For this machine, most development and security tools are organized under:

- `/etc/nixos/home/modules/packages/dev.nix`
- `/etc/nixos/home/modules/packages/tools.nix`
- `/etc/nixos/home/modules/packages/security.nix`
- `/etc/nixos/home/modules/agent/packages.nix`

After editing config, run:

```bash
sudo nixos-rebuild switch --flake /etc/nixos#nixos
```

## System Rebuild & Management

### Rebuilding

```bash
sudo nixos-rebuild switch --flake /etc/nixos#nixos
sudo nixos-rebuild boot --flake /etc/nixos#nixos
sudo nixos-rebuild dry-build --flake /etc/nixos#nixos
sudo nixos-rebuild build --flake /etc/nixos#nixos
```

Always use `--flake /etc/nixos#nixos`. The `#nixos` name is the `nixosConfigurations.nixos` output defined in `/etc/nixos/flake.nix`.

### Generations & Rollbacks

```bash
sudo nixos-rebuild list-generations
sudo nixos-rebuild switch --rollback
sudo nix-collect-garbage --delete-older-than 7d
```

### Updating Flake Inputs

```bash
sudo nix flake update /etc/nixos
sudo nix flake update /etc/nixos --update-input nixpkgs
sudo nix flake update /etc/nixos --update-input unstablepkgs
```

After updating inputs, rebuild with `nixos-rebuild switch`.

## WSL Notes

This is a WSL2 NixOS system, not a desktop NixOS host.

- The system uses `nix-community/NixOS-WSL` with `wsl.enable = true`.
- The WSL default user is `nixos`.
- `wsl.usbip.enable = true` is enabled for USB/IP workflows.
- Windows files are available under `/mnt/c`; avoid editing Linux project files through Windows paths when permissions or filesystem semantics matter.
- Windows VS Code is available as `/mnt/c/Soft/Microsoft VS Code/bin/code`.
- Systemd is running, but service assumptions should be checked because WSL is still a VM/container-like environment.
- No Hyprland, Flatpak, or graphical NixOS desktop stack is configured here.

## Nix Flake Structure

Key inputs in `/etc/nixos/flake.nix`:

- `nixpkgs` — stable `nixos-25.11`
- `unstablepkgs` — `nixos-unstable`, imported as `upkgs`
- `nixos-wsl` — NixOS-WSL module
- `home-manager` — `release-25.11`
- `sops-nix` — secrets management
- `pwndbg` — GDB plugin for reverse engineering
- `Neve` — Neovim distribution/package
- `local-skills`, `agent-skills`, `as0ler-skills`, `awesome-claude-skills`, `awesome-copilot-skills` — skill sources

Special variables available in config modules: `inputs`, `system`, and `upkgs`. Home Manager receives `inputs` and `upkgs` via `extraSpecialArgs`.

## Local Tooling

Use this machine as a development and security workstation inside WSL. Notable configured areas:

- Development: C/C++, Rust, Go, Java, Zig, Lua, Bash, Node.js, TypeScript, Nix tooling, language servers, formatters, and linters
- Security: nmap, rustscan, ffuf, feroxbuster, nuclei, sqlmap, tcpdump, tshark, mitmproxy, semgrep, gitleaks, trivy, yara, radare2, apktool, ghidra, volatility3, hashcat, john, ZAP
- Reverse/CTF: pwndbg, binwalk, upx, socat, qemu, jadx, Android platform tools, blutter, IDA/Pwno helper packages
- Containers: Podman enabled with Docker compatibility, `docker` command present, `distrobox` installed
- Agents/MCP: opencode, codex, claude-code, mcp-nixos, chrome-devtools, tmux-mcp, remote idalib/pwno MCP settings

## Troubleshooting

For detailed Nix operations, garbage collection, and common issues, read `references/nix_tips.md`.

Common scenarios:

- **Package not found**: use `mcp-nixos_nix` search first, then `nix search nixpkgs <name>` as fallback
- **Binary missing libraries**: use `nix-ld` support or run inside a proper `nix-shell`/`nix develop` environment
- **Build failure**: inspect logs with `nix log /nix/store/<hash>.drv`
- **Service behavior differs from native NixOS**: check `systemctl is-system-running` and specific service state because this is WSL2
- **USB/ADB issues**: remember `ADB_SERVER_SOCKET=tcp:127.0.0.1:5037` and `wsl.usbip.enable = true`
- **Windows interop path issues**: use Linux paths for Linux projects; use `/mnt/c` only when interacting with Windows files or Windows tools

## Environment Notes

- Programs live in `/nix/store/<hash>-<name>/bin/` and are symlinked into system or user profiles.
- System binaries are under `/run/current-system/sw/bin/`.
- User binaries are under `/etc/profiles/per-user/nixos/bin/`.
- The current account record uses a wrapped bash shell, while interactive bash sessions immediately exec fish.
- `nix-command` and `flakes` experimental features are enabled.
- `programs.nix-ld.enable = true` is enabled for running some non-Nix binaries.
