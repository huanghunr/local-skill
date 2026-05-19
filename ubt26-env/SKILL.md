---
name: ubt26-env
description: This skill should be used when CTF pwn, Linux binary debugging, glibc/libc matching, pwndbg/GDB sessions, Ubuntu-only package behavior, or exploit development tasks need to run inside the preconfigured Ubuntu distrobox named ubt26. It guides Claude to use tmux MCP for persistent interactive sessions and to prefer the ubt26 container whenever NixOS host tooling may differ from Ubuntu/glibc challenge targets.
---

# ubt26 Pwn 环境

## 目的

使用预配置的 `ubt26` distrobox 作为 CTF pwn、Linux ELF 调试、Ubuntu/glibc 敏感任务的默认执行环境。对交互式调试、长时间运行命令、GDB/pwndbg 会话、exploit 测试、下载和构建流程，优先使用 tmux MCP 保持持久终端状态。

需要确认工具路径、代理设置、libc 辅助工具用法或完整环境细节时，读取 `references/environment.md`。

## 触发条件

遇到以下请求时使用本 skill：

- 运行 `gdb`、`pwndbg`、`gdbserver`、exploit 脚本、`pwntools`、`ROPgadget`、`ropper`、`one_gadget`、`pwninit`、`seccomp-tools`、`checksec`、`patchelf`、`strace`、`ltrace`、`socat` 或 QEMU user-mode 工具。
- 解决 CTF pwn 题、复现 glibc heap 行为、调试 ELF、patch interpreter/RPATH、匹配 libc，或处理题目给出的 `libc.so.6`/`ld-linux` 文件。
- 构建或测试依赖 Ubuntu 包、Ubuntu 文件系统布局、Debian 包名、`apt`、`libc6-dbg`、multiarch gcc、Ubuntu glibc 语义的内容。
- 任务可能被 NixOS 宿主环境影响，例如动态链接器路径、库解析、包名、调试符号路径或二进制兼容性。
- 需要持久交互终端的长时间或多 pane 工作流。

不要将本 skill 用于纯源码编辑、纯文档任务、非 Linux 目标，或用户明确要求在 NixOS 宿主执行的工作流。

## 默认流程

1. 对非平凡 pwn 工作，启动或复用 tmux MCP 会话。
2. 用 `distrobox enter ubt26` 进入容器交互 shell。
3. 在容器 shell 内运行所有 pwn/debug 命令，不要在 NixOS 宿主直接运行题目二进制。
4. GitHub 或外部下载超时、EOF、速度异常时，设置 `127.0.0.1:7890` 代理变量。
5. 将 `/home/nixos/ubt26-home` 视为容器内用户 home 与工具配置位置。
6. 工具可用性不确定时，运行 `scripts/check_ubt26_pwn_env.sh` 验证环境。

快速非交互检查使用：

```sh
distrobox enter ubt26 -- bash -lc '<command>'
```

持久调试使用 tmux MCP 进入：

```sh
distrobox enter ubt26
```

随后在容器 pane 中直接执行命令。

## tmux MCP 使用规则

开始较大的 pwn 工作时，创建或复用专用 session，例如 `pwn-ubt26`。以下场景优先使用 tmux MCP，而不是普通 Bash：

- `gdb` 或 `pwndbg` 会话。
- 需要键盘交互的进程。
- 长时间包安装、源码构建、libc 下载或 exploit 爆破。
- 用 `socat`、`nc`、题目二进制或本地测试服务启动的服务。
- 需要多 pane 的工作流，例如一边跑 server，一边跑 exploit。
- 需要交互式shell，例如Frida，pwndbg等。

进入 `ubt26` 后，先确认提示符或命令输出确实处于容器内，再运行安装、修改或执行命令。查看长时间命令输出时，优先 capture pane，不要随意中断。

## 必须优先使用 Ubuntu 的场景

出现以下情况时，优先在 `ubt26` 中执行：

- 题目二进制动态链接 glibc，需要真实 Ubuntu loader/libc 行为。
- 任务需要 `apt install`、Debian 包名、Ubuntu debug symbols、`libc6-dbg`、`gcc-multilib` 或 `/lib/x86_64-linux-gnu` 路径。
- 工作流涉及 `patchelf`、`pwninit`、`ld-linux`、`libc.so.6` 或 RPATH/interpreter 行为。
- heap 利用行为、tcache/bin 内部结构、one_gadget 约束或 libc offset 很重要。
- Python wheel 或 Ruby gem 在 Ubuntu 中比 NixOS 中更容易安装。
- CTF writeup 或题目说明默认使用 Ubuntu/Kali 风格命令。

只有任务明确涉及 NixOS 配置、Nix 包、宿主服务，或明确要求使用宿主文件/命令时，才留在宿主环境。

## 常用命令

除非另有说明，在 `ubt26` 内运行：

```sh
checksec ./chall
pwninit
patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ./chall
gdb -q ./chall
python3 solve.py
ROPgadget --binary ./chall
ropper --file ./chall
one_gadget ./libc.so.6
seccomp-tools dump ./chall
```

交互使用 libc 工具：

```sh
libcdb
./add /path/to/libc.so.6
./identify /path/to/libc.so.6
./find puts f30 __libc_start_main_ret a83
```

```sh
libcai
./download 2.23-0ubuntu11.3_amd64
```

## 验证脚本

从宿主运行 bundled script 检查容器环境：

```sh
distrobox enter ubt26 -- bash /home/nixos/.config/opencode/skill/ubt26-pwn-env/scripts/check_ubt26_pwn_env.sh
```

按实际影响解释缺失项。缺少 `gdb`、`pwn`、`pwndbg`、`pwninit` 或 libc helper 目录时，将其视为 pwn 工作阻塞项。`ropper` 输出 Python escape sequence 的 `SyntaxWarning` 但仍能输出版本或 gadget 结果时，视为非阻塞。

## 代理规则

GitHub 和外部下载出现超时、EOF 或速度异常时，在容器命令或 tmux pane 内设置本地代理：

```sh
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

在执行 `git clone`、`curl`、`pipx`、`uv` 或 `gem` 之前应用这些变量。

## 安全与范围

不要默认下载全量 libc 数据库，除非用户明确要求或题目确实需要。优先用 `glibc-all-in-one` 做目标版本下载，或将题目给出的 libc 显式加入 `libc-database`。

不要在宿主上运行未知题目二进制；能在 `ubt26` 中运行时，一律放进 distrobox。将未知题目二进制视为不可信输入。

不要在容器工作时修改或重置宿主文件，除非用户明确要求。复制或引用题目文件时保持谨慎，避免破坏用户已有工作区改动。
