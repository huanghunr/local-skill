---
name: ctf-forensics
description: Provides digital forensics and signal analysis techniques for CTF challenges. Use when analyzing disk images, memory dumps, event logs, network captures, cryptocurrency transactions, steganography, PDF analysis, Windows registry, Volatility, PCAP, Docker images, coredumps, side-channel power traces, DTMF audio spectrograms, packet timing analysis, CD audio disc images, or recovering deleted files and credentials.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Forensics

## Additional Resources

- [3d-printing.md](references/3d-printing.md) - 3D printing forensics (PrusaSlicer binary G-code, QOIF, heatshrink)
- [windows.md](references/windows.md) - Windows forensics (registry, SAM, event logs, recycle bin, NTFS alternate data streams, USN journal, PowerShell history, Defender MPLog, WMI persistence, Amcache)
- [network.md](references/network.md) - Network forensics basics (tcpdump, TLS/SSL keylog decryption, TLS master key extraction from coredump, Wireshark, PCAP, SMB3 decryption, 5G/NR protocols, HTTP file upload exfiltration, split archive reassembly)
- [network-advanced.md](references/network-advanced.md) - Advanced network forensics (packet interval timing encoding, NTLMv2 hash cracking, TCP flag covert channel, DNS last-byte steganography, Brotli decompression bomb, SMB RID recycling, Timeroasting MS-SNTP, dnscat2 reassembly, RADIUS shared secret cracking)
- [peripheral-capture.md](references/peripheral-capture.md) - USB/HID/Bluetooth: mouse/pen drawing recovery, keyboard capture decoding, keyboard LED Morse exfiltration, arrow key navigation tracking, Bluetooth RFCOMM packet reassembly
- [disk-and-memory.md](references/disk-and-memory.md) - Core disk/memory: Volatility, disk mounting/carving, VM/OVA/VMDK, VMware snapshots, GIMP raw memory dump, coredumps, Windows KAPE triage, Android forensics, Docker container forensics, cloud storage forensics, BSON reconstruction, TrueCrypt/VeraCrypt
- [disk-advanced.md](references/disk-advanced.md) - Advanced disk/memory: deleted partitions, ZFS forensics, GPT GUID encoding, ransomware key recovery, WordPerfect macro XOR, minidump ISO 9660 recovery, APFS snapshot recovery, RAID 5 XOR recovery, HFS+ resource fork, Kyoto Cabinet hash DB, SQLite edit history
- [disk-recovery.md](references/disk-recovery.md) - Disk recovery: LUKS master key recovery, FemtoZip decompression, XFS filesystem reconstruction, nested matryoshka filesystem extraction, BTRFS subvolume/snapshot recovery, FAT16 free/deleted file recovery, ext2 orphaned inode recovery, corrupted ZIP header repair
- [steganography.md](references/steganography.md) - General stego: binary border stego, PDF multi-layer, SVG keyframes, PNG reorder, file overlays, GIF frame diff Morse code, Kitty terminal graphics, ANSI escape sequence stego, autostereogram solving, two-layer byte+line interleaving, multi-stream video container, progressive PNG layered XOR, QR code reconstruction
- [stego-image.md](references/stego-image.md) - Image stego: JPEG unused DQT table LSB, BMP bitplane QR extraction, image puzzle reassembly, F5 JPEG DCT ratio detection, PNG unused palette entry, QR code tile reconstruction, seed-based pixel permutation, JPEG thumbnail pixel-to-text mapping, conditional LSB, JPEG slack space, RGB parity stego
- [stego-advanced.md](references/stego-advanced.md) - Advanced stego part 1 (audio/signal): FFT frequency domain, DTMF audio, SSTV+LSB, DotCode barcode, custom dual-tone keypad, multi-track audio differential subtraction, cross-channel multi-bit LSB, audio FFT musical notes, audio metadata octal encoding, DeepSound with password cracking, audio waveform binary encoding, audio spectrogram hidden QR
- [stego-advanced-2.md](references/stego-advanced-2.md) - Advanced stego part 2 (video/image transform): video frame accumulation, reversed audio, video frame averaging, JPEG XL TOC permutation, Arnold's Cat Map descrambling, high-resolution SSTV custom FM demodulation, MJPEG FFD9 trailing byte, EXIF zlib + Stegano, PDF xref covert channel
- [linux-forensics.md](references/linux-forensics.md) - Linux/app forensics: log analysis, Docker image forensics, browser credentials (Chrome/Firefox), TFTP, TLS weak RSA, USB audio, Git directory recovery, KeePass v4 cracking, corrupted git blob repair, VBA macro Excel cell data to ELF extraction, Python in-memory source recovery via pyrasite
- [signals-and-hardware.md](references/signals-and-hardware.md) - Hardware signal decoding: VGA frame parsing, HDMI TMDS, DisplayPort 8b/10b + LFSR descrambler, Saleae Logic 2 UART, Flipper Zero .sub, side-channel power analysis (DPA), keyboard acoustic side-channel, CD audio disc stego (CIRC de-interleaving), caps-lock LED Morse from video, Linux input_event keylogger, serial UART from WAV audio, USB MIDI Launchpad

## When to Pivot

- If you recover an encrypted blob and the hard part becomes RSA, AES, or lattice work, switch to `/ctf-crypto`.
- If the evidence really points to malware staging, beacon config extraction, or packed samples, switch to `/ctf-malware`.
- If the artifact is a web app backup or API dump and the remaining problem is application logic, switch to `/ctf-web`.
- If the forensic evidence is really an encoding puzzle, steganography trick, or esoteric format rather than true forensics, switch to `/ctf-misc`.
- If you need to trace infrastructure, attribute actors, or investigate public records from forensic findings, switch to `/ctf-osint`.
- If the recovered artifact is a compiled binary or firmware that needs disassembly and analysis, switch to `/ctf-reverse`.

## Quick Start Commands

```bash
# File analysis
file suspicious_file
exiftool suspicious_file
binwalk suspicious_file
strings -n 8 suspicious_file
hexdump -C suspicious_file | head

# Disk forensics
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd
photorec image.dd

# Memory forensics (Volatility 3)
vol3 -f memory.dmp windows.info
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.filescan

# Network forensics
tshark -r capture.pcap -Y "tcp.stream eq X" -T fields -e tcp.payload
tshark --export-objects http,/tmp/objects -r capture.pcap

# Steganography
steghide extract -sf image.jpg
zsteg image.png
binwalk -e suspicious_file

# PDF analysis
exiftool document.pdf
pdftotext document.pdf -
strings document.pdf | grep -i flag
```

## Common Flag Locations

- PDF metadata fields (Author, Title, Keywords)
- Image EXIF data
- Deleted files (Recycle Bin `$R` files)
- Registry values
- Browser history / log file fragments
- Memory strings
- Appended data after file EOF markers
