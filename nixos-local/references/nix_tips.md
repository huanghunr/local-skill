# Nix/NixOS Operations Reference

## Searching for Packages

```bash
# Search nixpkgs for a package (flake-based system — use nix search)
nix search nixpkgs <keyword>

# Search with a specific flake input
nix search nixpkgs#<pkgname>

# Use the mcp-nixos_nix tool for up-to-date search results (preferred)
# Action: search, source: nixos, query: <keyword>
```

## Installing Packages (Temporary / Try-out)

```bash
# Try a package temporarily (shell session only)
nix-shell -p <pkgname>

# Try with unstable packages
nix-shell -I nixpkgs=https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz -p <pkgname>

# Enter a development shell from a shell.nix file
nix-shell
nix develop  # for flakes
```

## Adding Packages to System Configuration

Packages are managed declaratively. To add packages:

1. **For system-wide packages** — edit `/etc/nixos/nixos/configuration.nix`
   ```nix
   environment.systemPackages = with pkgs; [
     # add package here
   ];
   ```

2. **For user packages** — edit `/etc/nixos/home/home.nix`
   ```nix
   home.packages = with pkgs; [
     # add package here
   ];
   ```

3. For unstable packages, use `upkgs.<name>` (the unstablepkgs input is available as `upkgs`)

## Rebuilding the System

```bash
# Rebuild and switch to new configuration (MUST run as root)
sudo nixos-rebuild switch --flake /etc/nixos#nixos

# Rebuild and boot into it on next restart
sudo nixos-rebuild boot --flake /etc/nixos#nixos

# Dry-run (check what will change without applying)
sudo nixos-rebuild dry-build --flake /etc/nixos#nixos

# Build without switching (just build, don't activate)
sudo nixos-rebuild build --flake /etc/nixos#nixos
```

**IMPORTANT**: `nixos-rebuild switch` requires root privileges. The flake reference is `/etc/nixos#nixos` where `nixos` is the `nixosConfigurations` name defined in the flake.

## Managing Generations & Rollbacks

```bash
# List system generations
sudo nix-env --list-generations -p /nix/var/nix/profiles/system
sudo nixos-rebuild list-generations

# Rollback to previous generation
sudo nixos-rebuild switch --rollback

# Rollback to a specific generation
sudo nixos-rebuild switch --flake /etc/nixos#nixos --rollback  # one step
# OR use nix-env:
sudo /nix/var/nix/profiles/system-<N>-link/bin/switch-to-configuration switch
```

## Garbage Collection

```bash
# Delete old generations (keep last N)
sudo nix-collect-garbage --delete-older-than 7d

# Aggressive cleanup
sudo nix-collect-garbage -d

# Check what would be deleted
sudo nix-collect-garbage --dry-run
```

## Home Manager

Home Manager is integrated via the NixOS module. It rebuilds as part of `nixos-rebuild switch`.

```bash
# Show home-manager generations
home-manager generations

# List home-manager packages
home-manager packages
```

## Flake Operations

```bash
# Update flake inputs
nix flake update

# Update a specific input only
nix flake update --update-input nixpkgs

# Show flake metadata
nix flake metadata /etc/nixos

# Check flake structure
nix flake show /etc/nixos
```

## Troubleshooting

```bash
# Check what provides a command (for missing deps)
nix-locate <command>

# Run a binary that has missing dynamic libraries (nix-alien)
nix-alien <command>

# Enter a shell with libraries for an unpatched binary
nix-alien-ld <binary>

# Show package build log on failure
nix log /nix/store/<hash>-<pkgname>.drv

# Check package dependencies
nix-store --query --references /nix/store/<hash>-<pkgname>
nix-store --query --tree $(which <program>)
```

## Flatpak (via nix-flatpak)

```bash
# The nix-flatpak module provides Flatpak integration
flatpak search <app>
flatpak install <remote> <app>
flatpak run <app-id>
```

## Key Nix Principles

1. **Immutable**: `/nix/store` is read-only; packages are built from derivations
2. **Declarative**: System config is in `.nix` files, not imperative commands
3. **Reproducible**: Same inputs produce the same outputs
4. **Atomic updates**: System switches are atomic — broken config won't break the running system
5. **Rollbacks**: Every generation is preserved; easy to go back

## Environment Quirks

- Binaries are in `/run/current-system/sw/bin/` (system) and `/etc/profiles/per-user/<user>/bin/` (user)
- No `/usr/bin` or `/usr/lib` — standard FHS paths don't exist on NixOS
- `LD_LIBRARY_PATH` is generally not set; libraries are found via RPATH in ELF headers
- Use `patchelf` to modify RPATH of binaries manually if needed
