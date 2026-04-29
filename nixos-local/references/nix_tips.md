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

## Using Unstable (Latest) Packages

This system has `unstablepkgs` as a flake input (`nixos-unstable` branch). It is imported as `upkgs` and available in all config modules.

### Try an Unstable Package in Shell

```bash
# Method 1: Using the flake input directly
nix shell nixpkgs/nixos-unstable#<pkgname>

# Method 2: Using nixpkgs with unstable tarball
nix-shell -I nixpkgs=https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz -p <pkgname>

# Method 3: Build and run (flake-based)
nix run nixpkgs/nixos-unstable#<pkgname>

# Method 4: Enter a dev shell with unstable channel
nix develop nixpkgs/nixos-unstable#<pkgname>
```

### Add Unstable Package to Config Permanently

The `upkgs` variable is passed via `specialArgs` in the flake. Use it in config files:

```nix
# In /etc/nixos/home/home.nix (home.packages) or /etc/nixos/nixos/configuration.nix (environment.systemPackages):
{ upkgs, ... }:
{
  # Add to the packages list:
  environment.systemPackages = with pkgs; [
    some-stable-pkg
  ] ++ (with upkgs; [
    some-latest-pkg    # this one comes from unstable
  ]);
}
```

For home-manager packages:
```nix
{ upkgs, ... }:
{
  home.packages = with pkgs; [
    stable-tool
  ] ++ (with upkgs; [
    latest-tool        # from unstable
  ]);
}
```

### Override a Single Package with Unstable Version

If you need a specific package from unstable without pulling in its unstable dependencies (risky):

```nix
{ pkgs, upkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    # Use unstable version of a package, still linking against stable libs
    (upkgs.some-pkg.override { /* optional overrides */ })
  ];
}
```

**Note**: Mixing stable and unstable packages can cause dependency conflicts. If a package from `upkgs` fails to build, try using all its dependencies from `upkgs` too, or build a custom derivation (see below).

## Building Custom Packages (Writing Nix Derivations)

When a package is not in nixpkgs, or you need a custom build, write a Nix derivation.

### Quick: Build from a Flake

Create a `flake.nix` in a project directory:

```nix
{
  description = "Custom package build";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    packages.${system}.default = pkgs.stdenv.mkDerivation {
      pname = "my-tool";
      version = "1.0.0";

      src = pkgs.fetchFromGitHub {
        owner = "some-owner";
        repo = "some-repo";
        rev = "v1.0.0";
        sha256 = "";  # nix will tell you the hash on first build
      };

      buildInputs = with pkgs; [ cmake pkg-config ];

      # For Go/Rust projects, use buildGoModule/buildRustPackage instead
    };
  };
}
```

Build it:
```bash
nix build    # builds and symlinks ./result
nix run      # builds and runs
```

### Simple Derivation for a Script or Binary

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "my-script";
  version = "0.1";

  src = ./.;  # local source directory

  installPhase = ''
    mkdir -p $out/bin
    cp my-script.sh $out/bin/my-script
    chmod +x $out/bin/my-script
  '';
}
```

Save as `default.nix`, then:
```bash
nix-build          # build
nix-shell          # enter environment
```

### Override an Existing Package (Custom Build Flags / Patches)

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.some-package.overrideAttrs (oldAttrs: {
  # Change version/source
  version = "newer-version";
  src = pkgs.fetchFromGitHub { /* ... */ };

  # Add build flags
  buildInputs = oldAttrs.buildInputs ++ [ pkgs.some-extra-lib ];

  # Apply a patch
  patches = (oldAttrs.patches or []) ++ [ ./my-fix.patch ];

  # Add extra cmake/meson flags
  cmakeFlags = (oldAttrs.cmakeFlags or []) ++ [ "-DENABLE_FEATURE=ON" ];
})
```

Build: `nix-build -E 'with import <nixpkgs> {}; callPackage ./override.nix {}'`

### Language-Specific Build Helpers

Nixpkgs provides helpers for common ecosystems:

```nix
# Python
python3Packages.buildPythonApplication { /* ... */ }

# Go
buildGoModule {
  vendorHash = "";  # nix will tell you
  /* ... */
}

# Rust
rustPlatform.buildRustPackage {
  cargoHash = "";   # nix will tell you
  /* ... */
}

# Node.js
buildNpmPackage {
  npmDepsHash = ""; # nix will tell you
  /* ... */
}
```

### Getting the Hash Right

On first build, use a dummy hash and nix will report the expected one:

```bash
# Set hash to empty or lib.fakeSha256, build, and nix will error with the correct hash
nix build 2>&1 | grep "got:" | head -1
# or
nix-build 2>&1 | grep "got:" | head -1
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
