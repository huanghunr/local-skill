# System Information

## Hardware / VM

- **Platform**: WSL2 virtualization on Microsoft hypervisor
- **CPU**: 13th Gen Intel Core i9-13980HX, 24 vCPUs exposed to WSL
- **RAM**: 15Gi total, about 10Gi available at collection time
- **Swap**: 15Gi
- **Root disk**: `/dev/sdd`, 1007G total, 823G available at collection time
- **Windows C drive**: mounted at `/mnt/c`, 954G total, 292G available at collection time
- **Architecture**: `x86_64-linux`

## OS

- **Distribution**: NixOS 25.11 (Xantusia)
- **Build ID**: `25.11.20260309.44bae27`
- **Kernel**: `6.6.87.2-microsoft-standard-WSL2`
- **Hostname**: `nixos`
- **Virtualization**: `wsl`
- **Chassis**: `container`
- **Systemd state at collection time**: `running`

## User, Shell, Editor

- **User**: `nixos`
- **Home**: `/home/nixos`
- **Account shell**: `/nix/store/8m1ndq2ihkarf43xpx5jjw51ynjzf7iq-wrapped-bash/wrapper`
- **Interactive shell behavior**: bash interactive init execs fish unless already launched from fish
- **Fish**: enabled via Home Manager with `z` plugin and aliases `ll = ls -lan`, `cl = clear`
- **Editor**: Neovim (`nvim`) from user profile, Vim system-wide, Windows VS Code at `/mnt/c/Soft/Microsoft VS Code/bin/code`

## Key Installed Tools

| Category | Tools |
|----------|-------|
| Package management | `nix`, `nix-shell`, `nixos-rebuild`, `home-manager` via integrated module |
| Version control | `git`, GitHub CLI `gh` |
| Shell/editor | `fish`, `bash`, `nvim`, `vim`, `fzf`, `tmux`, `yazi` |
| Containers | `podman`, Docker-compatible `docker`, `distrobox` |
| Network | `curl`, `wget`, `socat`, `nmap`, `rustscan`, `tcpdump`, `tshark`, `mitmproxy` |
| Development | GCC, GDB, LLDB, clang-tools, CMake, Rust, Go, Java/JDK 25, Gradle, Maven, Node.js, TypeScript, Zig tooling, Lua tooling |
| Nix development | `nixd`, `statix`, `deadnix`, `nixfmt`, `devenv` |
| Security | `ffuf`, `feroxbuster`, `gobuster`, `nuclei`, `sqlmap`, `semgrep`, `gitleaks`, `trivy`, `syft`, `grype`, `yara`, `sslscan`, `testssl`, `ssh-audit`, `zap` |
| Reverse / forensics | `radare2`, `apktool`, `ghidra`, `volatility3`, `exiftool`, `foremost`, `binwalk`, `upx`, `qemu`, `pwndbg` |
| Android / mobile | Android platform tools, `jadx`, `blutter`, `ADB_SERVER_SOCKET=tcp:127.0.0.1:5037` |
| Agent/MCP | `opencode`, `codex`, `claude-code`, `mcp-nixos`, `chrome-devtools`, `tmux-mcp`, idalib/pwno MCP settings |

## Services and System Features

- **systemd**: running
- **sshd**: installed but inactive at collection time
- **Podman**: enabled with Docker compatibility (`virtualisation.podman.dockerCompat = true`)
- **WSL USB/IP**: enabled via `wsl.usbip.enable = true`
- **nix-ld**: enabled via `programs.nix-ld.enable = true`
- **Nix flakes**: enabled via `nix.settings.experimental-features = [ "nix-command" "flakes" ]`
- **Unfree packages**: allowed via `nixpkgs.config.allowUnfree = true`

## Nix Flake Setup

The system is managed via `/etc/nixos/flake.nix`, which resolves to the dirty git tree `/home/nixos/nixos-config` at collection time.

Key files:

- `/etc/nixos/flake.nix` — flake inputs and `nixosConfigurations.nixos`
- `/etc/nixos/configuration.nix` — top-level NixOS config, imports `./nixos`
- `/etc/nixos/nixos/default.nix` — imports system modules `podman.nix` and `secrets.nix`
- `/etc/nixos/nixos/podman.nix` — container and Podman setup
- `/etc/nixos/home/home.nix` — Home Manager entry for user `nixos`
- `/etc/nixos/home/modules/packages/` — development, tools, security, fish, and yazi packages
- `/etc/nixos/home/modules/agent/` — agent packages and MCP configuration

Key inputs:

- `nixpkgs`: `github:NixOS/nixpkgs/nixos-25.11`
- `unstablepkgs`: `github:nixos/nixpkgs/nixos-unstable`, imported as `upkgs`
- `nixos-wsl`: `github:nix-community/NixOS-WSL/main`
- `home-manager`: `github:nix-community/home-manager/release-25.11`, follows `nixpkgs`
- `sops-nix`: secrets management, follows `nixpkgs`
- `pwndbg`: GDB plugin input
- `Neve`: Neovim package/distribution input
- `local-skills`, `agent-skills`, `as0ler-skills`, `awesome-claude-skills`, `awesome-copilot-skills`: skill sources

NixOS output:

- `nixosConfigurations.nixos`
- `system = "x86_64-linux"`
- `system.stateVersion = "25.11"`
- `wsl.enable = true`
- `wsl.defaultUser = "nixos"`

## WSL-Specific Behavior

- Treat this as a NixOS system running inside WSL2, not as a native desktop NixOS install.
- Expect Microsoft WSL kernel behavior and Windows interop paths under `/mnt/c`.
- Prefer Linux filesystem paths under `/home/nixos` for repositories and build outputs.
- Use `/mnt/c` only for Windows files or Windows executables such as VS Code.
- Check service state before assuming daemons are active; `sshd` was inactive at collection time.
- USB and Android workflows may depend on Windows-side USB/IP or ADB server state.

## Nix Channels

No user channels are required for normal operation. The machine is flake-based and should use `/etc/nixos#nixos` for rebuilds.
