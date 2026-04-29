# local-skill

本地 Agent Skills 集合。

## 来源

以下 CTF 技能来自 [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills.git) 项目，经过以下修改：

1. **精简 SKILL.md**：去除与 `references/` 目录重复的深层技术描述，仅保留方向性判断和工具使用指引
2. **标准化目录结构**：将技术文档移至 `references/` 子目录，新增 `scripts/` 和 `assets/` 目录

## 包含的技能

| 技能 | 说明 |
|------|------|
| `solve-challenge` | CTF 挑战分派与分类入口 |
| `ctf-web` | Web 漏洞利用 (XSS, SQLi, SSTI, SSRF, JWT 等) |
| `ctf-pwn` | 二进制漏洞利用 (栈溢出, 堆利用, ROP, 内核 等) |
| `ctf-reverse` | 逆向工程 (二进制分析, 反调试, 混淆, WASM 等) |
| `ctf-crypto` | 密码学攻击 (RSA, AES, ECC, 格密码, PRNG 等) |
| `ctf-forensics` | 数字取证 (磁盘/内存分析, 隐写, PCAP, 信号分析 等) |
| `ctf-misc` | 杂项 (编码谜题, pyjail/bash jail, Z3约束求解, DNS, RF/SDR 等) |
| `ctf-osint` | 开源情报 (社交媒体, 地理位置, DNS, Google Dorking 等) |
| `ctf-malware` | 恶意软件分析 (混淆脚本, C2流量, PE/.NET, YARA 等) |
| `ctf-ai-ml` | AI/ML 攻防 (对抗样本, 模型提取, Prompt注入, LLM越狱 等) |
| `ctf-writeup` | CTF Writeup 生成器 |

## 许可证

MIT License（与原项目一致）

## 原项目

https://github.com/ljagiello/ctf-skills.git
