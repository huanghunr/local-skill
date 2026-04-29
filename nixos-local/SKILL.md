---
name: nixos-local
description: |
  This skill provides knowledge about this specific NixOS machine for system operations.
  Use when the user asks about installing packages, searching nixpkgs, rebuilding the
  NixOS system, managing generations, using nix-shell, debugging Nix build failures,
  navigating the flake configuration, or understanding the local environment.
  This skill should be used for any task involving Nix package management, NixOS
  system administration, or environment-specific tool usage on this machine.
---

# NixOS Local Machine Reference

## Overview

This skill covers the NixOS 25.11 (Xantusia) machine. The system is managed via a flake at `/etc/nixos/flake.nix`, with home-manager integrated for user configuration. The compositor is Hyprland 0.52, shell is fish, and editor is neovim.

## Quick Reference

- **System flake**: `/etc/nixos/flake.nix`
- **System config**: `/etc/nixos/nixos/configuration.nix`
- **Home config**: `/etc/nixos/home/home.nix`
- **Rebuild command**: `sudo nixos-rebuild switch --flake /etc/nixos#nixos`
- **User**: `huanghunr`
- **Arch**: `x86_64-linux`

When system details are needed (hardware, tools, services), read `references/system_info.md`.

## Package Operations

### Searching for Packages

Use the `mcp-nixos_nix` tool for up-to-date search results. It is always preferred over `nix search` because it returns current channel data.

For command-line fallback:
```bash
nix search nixpkgs <keyword>
nix search nixpkgs#<pkgname>
```

### Trying a Package Temporarily

```bash
nix-shell -p <pkgname>                          # stable channel
nix-shell -p <pkgname1> <pkgname2>              # multiple packages
nix shell nixpkgs/nixos-unstable#<pkgname>      # try unstable version
nix develop                                      # flake-based dev shell (from current dir)
```

### Getting the Latest Version (Unstable Channel)

This system has `unstablepkgs` (`nixos-unstable`) as a flake input, imported as `upkgs`. When you need the bleeding-edge version of a tool:

- **Try in shell**: `nix shell nixpkgs/nixos-unstable#<pkgname>`
- **Add to config**: Use `upkgs.<name>` in `configuration.nix` or `home.nix` — e.g. `(with upkgs; [ <pkgname> ])`
- **Caveat**: Mixing stable/unstable can cause dependency conflicts. If a build fails, use all unstable deps or write a custom derivation.

See `references/nix_tips.md` > "Using Unstable (Latest) Packages" for full details.

### Adding a Package Permanently

System-wide packages go in `/etc/nixos/nixos/configuration.nix` under `environment.systemPackages`.
User packages go in `/etc/nixos/home/home.nix` under `home.packages`.
For unstable packages, use `upkgs.<name>` — the `upkgs` variable is passed via `specialArgs`.

After editing the config, run: `sudo nixos-rebuild switch --flake /etc/nixos#nixos`

### Building a Package from Source

When a package is not in nixpkgs or needs custom build flags, write a Nix derivation:

```bash
# Quick: use mkDerivation in a flake or default.nix
nix build   # build and symlink ./result
nix run     # build and execute
```

Language-specific helpers are available: `buildGoModule`, `buildRustPackage`, `buildPythonApplication`, `buildNpmPackage`.

See `references/nix_tips.md` > "Building Custom Packages" for derivations, overrides, and hash handling.

### Installing via Flatpak

If a package is unavailable or broken in nixpkgs, Flatpak is available:
```bash
flatpak search <app>
flatpak install flathub <app-id>
```

## System Rebuild & Management

### Rebuilding

```bash
sudo nixos-rebuild switch --flake /etc/nixos#nixos      # apply now
sudo nixos-rebuild boot --flake /etc/nixos#nixos        # apply on next boot
sudo nixos-rebuild dry-build --flake /etc/nixos#nixos   # check without applying
```

Always use `--flake /etc/nixos#nixos`. The `#nixos` refers to the `nixosConfigurations.nixos` entry in the flake outputs.

### Generations & Rollbacks

```bash
sudo nixos-rebuild list-generations                    # list generations
sudo nixos-rebuild switch --rollback                   # go back one generation
sudo nix-collect-garbage --delete-older-than 7d        # clean old generations
```

### Updating Flake Inputs

```bash
sudo nix flake update /etc/nixos                        # update all inputs
sudo nix flake update /etc/nixos --update-input nixpkgs # update nixpkgs only
```

After updating inputs, rebuild with `nixos-rebuild switch`.

## Nix Flake Structure

The flake has these key inputs:
- `nixpkgs` — stable `nixos-25.11`
- `unstablepkgs` — `nixos-unstable` (for select bleeding-edge packages)
- `home-manager` — `release-25.11`
- `hyprland` — Wayland compositor
- `sops-nix` — secrets management
- `nix-alien` — run unpatched binaries
- `nix-flatpak` — Flatpak integration
- `nur` — Nix User Repository

Special variables available in config modules: `inputs` (all flake inputs), `upkgs` (unstable pkgs import).

## Troubleshooting

For detailed Nix operations, garbage collection, and common issues, read `references/nix_tips.md`.

Common scenarios:

- **Package not found**: Search with `nix search nixpkgs <name>` or use the mcp-nixos_nix tool
- **Binary won't run (missing libs)**: Use `nix-alien <binary>` or `nix-alien-ld <binary>`
- **Build failure**: Check the log with `nix log /nix/store/<hash>.drv`
- **Need to debug a package**: `nix-shell -p <pkg>` then inspect
- **Shell not finding a command**: Commands aren't in standard FHS paths; check `/run/current-system/sw/bin/`

## Environment Notes

- No `/usr/bin`, `/usr/lib` — NixOS does not follow FHS
- Programs are in `/nix/store/<hash>-<name>/bin/`, symlinked to profiles
- System binaries: `/run/current-system/sw/bin/`
- User binaries: `/etc/profiles/per-user/huanghunr/bin/`
- `LD_LIBRARY_PATH` is not used; RPATH in ELF headers handles library resolution
- SSH daemon is running (for remote access)
