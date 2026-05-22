# Nix/NixOS WSL Operations Reference

## Searching for Packages and Options

Prefer the `mcp-nixos_nix` tool for current package and option data.

Command-line fallback:

```bash
nix search nixpkgs <keyword>
nix search nixpkgs#<pkgname>
nix flake show nixpkgs#<attr>
```

For NixOS/Home Manager options, use `mcp-nixos_nix` with option search before guessing option names.

## Temporary Package Environments

Use `nix-shell` or `nix shell` for one-off commands:

```bash
nix-shell -p python3 nodejs gcc
nix shell nixpkgs#ripgrep
nix shell nixpkgs/nixos-unstable#<pkgname>
```

Use `nix develop` for project flakes:

```bash
nix develop
nix develop nixpkgs/nixos-unstable#<pkgname>
```

For multi-package environments, create a local `shell.nix`:

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [ python3 nodejs gcc pkg-config openssl ];
  shellHook = ''
    export PYTHONPATH="$PWD:$PYTHONPATH"
  '';
}
```

## Permanent Package Changes

System-wide packages:

```nix
# /etc/nixos/configuration.nix or a module imported by /etc/nixos/nixos/default.nix
environment.systemPackages = with pkgs; [
  wget
  vim
];
```

User packages:

```nix
# /etc/nixos/home/home.nix or a module under /etc/nixos/home/modules/
home.packages = with pkgs; [
  ripgrep
  tmux
];
```

This machine keeps most user tools in these modules:

- `/etc/nixos/home/modules/packages/dev.nix`
- `/etc/nixos/home/modules/packages/tools.nix`
- `/etc/nixos/home/modules/packages/security.nix`
- `/etc/nixos/home/modules/agent/packages.nix`

## Unstable Packages

The flake imports `unstablepkgs` as `upkgs`:

```nix
upkgs = import inputs.unstablepkgs {
  system = system;
  config.allowUnfree = true;
};
```

Use it in modules that receive `upkgs`:

```nix
{ pkgs, upkgs, ... }:
{
  home.packages = with pkgs; [ stable-tool ] ++ [
    upkgs.latest-tool
  ];
}
```

Prefer using one package set consistently when dependency conflicts appear.

## Rebuilding the WSL NixOS System

Use the flake output `nixosConfigurations.nixos`:

```bash
sudo nixos-rebuild switch --flake /etc/nixos#nixos
sudo nixos-rebuild dry-build --flake /etc/nixos#nixos
sudo nixos-rebuild build --flake /etc/nixos#nixos
```

Use `switch` to apply changes immediately. Use `dry-build` before risky changes.

## Updating Inputs

```bash
sudo nix flake update /etc/nixos
sudo nix flake update /etc/nixos --update-input nixpkgs
sudo nix flake update /etc/nixos --update-input unstablepkgs
sudo nix flake update /etc/nixos --update-input home-manager
sudo nix flake update /etc/nixos --update-input nixos-wsl
```

Rebuild after updates:

```bash
sudo nixos-rebuild switch --flake /etc/nixos#nixos
```

## Generations, Rollbacks, and Garbage Collection

```bash
sudo nixos-rebuild list-generations
sudo nixos-rebuild switch --rollback
sudo nix-collect-garbage --delete-older-than 7d
sudo nix-collect-garbage --dry-run
```

Home Manager is integrated into the NixOS module, so normal `nixos-rebuild switch` applies user config too.

## WSL Considerations

This machine uses `nix-community/NixOS-WSL`:

```nix
nixos-wsl.nixosModules.default
{
  system.stateVersion = "25.11";
  wsl.enable = true;
  wsl.defaultUser = "nixos";
}
```

Important WSL behavior:

- Use `/home/nixos` for Linux repositories and build outputs.
- Use `/mnt/c` for Windows files or Windows executables only.
- Check service status before assuming a daemon is active.
- `systemctl is-system-running` can be useful, but WSL still differs from native NixOS boot behavior.
- Windows-side tools can affect USB, ADB, browser, and debugger workflows.

## USB and Android

Current config includes:

```nix
wsl.usbip.enable = true;
environment.variables.ADB_SERVER_SOCKET = "tcp:127.0.0.1:5037";
```

For Android or USB workflows, verify both Linux-side tools and Windows-side attachment/server state.

## Containers

Podman is enabled with Docker compatibility:

```nix
virtualisation.containers.enable = true;
virtualisation.podman.enable = true;
virtualisation.podman.dockerCompat = true;
```

Use either `podman` or the Docker-compatible `docker` command. If a container fails under WSL, check cgroup/systemd behavior and filesystem paths.

## Running Non-Nix Binaries

`programs.nix-ld.enable = true` is enabled. Prefer packaging dependencies with Nix or using `nix-shell`/`nix develop`; use nix-ld as a compatibility aid for external binaries.

For missing library diagnostics:

```bash
ldd ./binary
nix log /nix/store/<hash>.drv
nix-store --query --references /nix/store/<hash>-<pkg>
```

## Build Troubleshooting

Useful commands:

```bash
nix log /nix/store/<hash>.drv
nix build --show-trace
nixos-rebuild dry-build --flake /etc/nixos#nixos --show-trace
nix-store --query --tree $(which <program>)
```

Common fixes:

- Add missing native build tools to `nativeBuildInputs` or `packages` in `mkShell`.
- Use `pkg-config` and relevant `*-dev` libraries from nixpkgs for C/C++ builds.
- Avoid mixing Windows paths with Linux build tooling.
- Use `upkgs` consistently when unstable dependencies are required.

## Agent and MCP Configuration

Agent and MCP setup lives under `/etc/nixos/home/modules/agent/`.

Notable configured servers/tools:

- `mcp-nixos` via `uv tool run mcp-nixos`
- `chrome-devtools` via `npx` and packaged Google Chrome
- `tmux-mcp` via `npx`
- `idalib-mcp` remote at `http://127.0.0.1:8745/mcp`
- `pwno-mcp` remote at `http://127.0.0.1:5500/mcp`
- Disabled or optional entries include `ida-pro-mcp`, `scrapling-mcp`, and `mcp_windbg_http`

When debugging agent tooling, inspect `/etc/nixos/home/modules/agent/packages.nix` and `/etc/nixos/home/modules/agent/mcp.nix` first.
