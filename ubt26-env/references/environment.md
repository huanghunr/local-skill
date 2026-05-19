# ubt26 Pwn 环境参考

## 容器进入方式

使用 `distrobox enter ubt26` 进入 Ubuntu 容器。对需要持久状态的交互式任务优先使用 tmux MCP，例如 GDB、pwndbg、长时间下载、exploit 调试会话。

快速非交互命令使用：

```sh
distrobox enter ubt26 -- bash -lc '<command>'
```

GitHub 或外部下载慢/超时时设置代理：

```sh
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

## 已安装工具

系统工具包括 `gcc`、`g++`、`make`、`cmake`、`gdb`、`gdbserver`、`git`、`curl`、`file`、`binutils`、`patchelf`、`strace`、`ltrace`、`socat`、`netcat-openbsd`、`qemu-user`、`checksec`、`nasm`、`yasm`。

Pwn 工具包括 `pwntools`、`ROPgadget`、`ropper`、`pwninit`、`one_gadget`、`seccomp-tools`、`seccomp`、`ceccomp`、`libc-database`、`glibc-all-in-one`。

GDB 通过以下文件加载 pwndbg：

```text
/home/nixos/ubt26-home/.local/src/pwndbg/gdbinit.py
```

用户 PATH 增量写在 `/home/nixos/ubt26-home/.bashrc`：

```sh
/home/nixos/ubt26-home/.local/bin
/home/nixos/ubt26-home/.local/share/gem/ruby/3.3.0/bin
```

## libc 辅助工具

`libc-database` 路径：

```text
/home/nixos/ubt26-home/.local/src/libc-database
```

`glibc-all-in-one` 路径：

```text
/home/nixos/ubt26-home/.local/src/libc-all-in-one
```

交互 bash 中配置了别名：

```sh
libcdb
libcai
```

`glibc-all-in-one` 的 list 文件已初始化。仅在需要时下载目标 libc，例如：

```sh
cd "$LIBC_ALL_IN_ONE"
./download 2.23-0ubuntu11.3_amd64
```

`libc-database` 已添加容器本地 libc。遇到题目给出的 libc 时显式加入：

```sh
cd "$LIBC_DATABASE"
./add /path/to/libc.so.6
./identify /path/to/libc.so.6
```

## 验证

通过容器运行 bundled script：

```sh
distrobox enter ubt26 -- bash /home/nixos/.config/opencode/skill/ubt26-pwn-env/scripts/check_ubt26_pwn_env.sh
```
