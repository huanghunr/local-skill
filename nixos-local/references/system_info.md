# System Information

## Hardware

- **CPU**: 13th Gen Intel Core i9-13980HX (32 cores)
- **RAM**: 30Gi total, ~22Gi available
- **Disk**: 360G NVMe (/dev/nvme1n1p4), 207G used, 135G free
- **Architecture**: x86_64-linux

## OS

- **Distribution**: NixOS 25.11 (Xantusia), kernel 6.18.20
- **Version ID**: 25.11, build 20260401.bcd464c
- **Hostname**: nixos

## Shell & Editor

- **Default shell**: fish (at `/run/current-system/sw/bin/fish`)
- **Editor**: neovim (`nvim`), also vim and VS Code (`code`) available

## Key Installed Tools

| Category | Tools |
|----------|-------|
| Package mgmt | `nix`, `nix-shell`, `nixos-rebuild`, `flatpak` |
| Version control | `git` |
| Containers | `podman` |
| Network | `curl`, `wget` |
| Security/secrets | `sops` (v3.12.1) |
| Monitoring | `btop`, `htop` (likely) |
| Terminal | `zellij` (multiplexer), `fzf` (fuzzy finder) |
| WM/Compositor | Hyprland 0.52.1 |

## Services

- **sshd**: active (SSH server running)
- **Desktop**: Hyprland (Wayland compositor)

## Nix Flake Setup

The system is managed via a flake at `/etc/nixos/flake.nix`. Key inputs:

- `nixpkgs`: `nixos-25.11` (stable)
- `unstablepkgs`: `nixos-unstable` (select packages use this)
- `home-manager`: `release-25.11` (follows nixpkgs)
- `hyprland`: Hyprland Wayland compositor + plugins (`hyprgrass`)
- `sops-nix`: secrets management
- `nix-flatpak`: Flatpak integration
- `noctalia`: noctalia-shell (home-manager module)
- `nur`: Nix User Repository
- `nix-alien`: Run unpatched binaries on NixOS
- `pwndbg`: GDB plugin for reverse engineering
- `ctf-skills`, `awesome-claude-skills`, `agent-skills`: skill collections

Configuration files (relative to flake root `/etc/nixos/`):
- `nixos/configuration.nix` — system-level NixOS config
- `home/home.nix` — user-level home-manager config (user: `huanghunr`)

## Nix Channels

No channels (flake system). Registry includes common flake shortcuts.
