---
name: ctf-osint
description: Provides open source intelligence techniques for CTF challenges. Use when gathering information from public sources, social media, geolocation, DNS records, username enumeration, reverse image search, Google dorking, Wayback Machine, Tor relays, FEC filings, or identifying unknown data like hashes and coordinates.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for OSINT lookups.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF OSINT

## Additional Resources

- [social-media.md](references/social-media.md) - Twitter/X (user IDs, Snowflake timestamps, Nitter, Wayback CDX), Tumblr (blog checks, post JSON, avatars), BlueSky search + API, Unicode homoglyph steganography, Discord API, username OSINT (namechk, whatsmyname), username metadata mining, multi-platform chains, Strava fitness route OSINT
- [geolocation-and-media.md](references/geolocation-and-media.md) - Image analysis, reverse image search (Google Lens, Baidu for China), reflected/mirrored text reading, geolocation (railroad signs, infrastructure maps, MGRS), Google Plus Codes, EXIF/metadata, hardware identification, newspaper archives, IP geolocation, Google Street View panorama matching, What3Words micro-landmark matching, Overpass Turbo spatial queries
- [web-and-dns.md](references/web-and-dns.md) - Google dorking (including TBS image filters), Google Docs/Sheets enumeration, DNS recon (TXT, zone transfers), Wayback Machine, FEC research, Tor relay lookups, GitHub repository analysis, Telegram bot investigation, WHOIS investigation (reverse WHOIS, historical WHOIS, IP/ASN lookup), fake service banner detection via nmap fingerprinting, Shodan SSH fingerprint lookup

## When to Pivot

- If you already have the files or packets locally and now need extraction or carving, switch to `/ctf-forensics`.
- If the task becomes active exploitation of a live HTTP service, switch to `/ctf-web`.
- If you uncover malware samples, beacons, or suspicious binaries during attribution, switch to `/ctf-malware`.

## Quick Start Commands

```bash
# DNS recon
dig -t any target.com
dig -t txt target.com
dig axfr @ns.target.com target.com
whois target.com

# Image metadata
exiftool image.jpg
identify -verbose image.jpg | head -30

# Web archive
curl "https://web.archive.org/web/20230101*/target.com"

# Username lookup
curl -s "https://whatsmyname.app/api/lookup?username=<user>"

# Shodan
shodan search "hostname:target.com"
shodan host <ip>
```

## String Identification

- 40 hex chars -> SHA-1 (Tor fingerprint)
- 64 hex chars -> SHA-256
- 32 hex chars -> MD5

## Key Techniques

- **Twitter/X:** Persistent numeric User ID at `https://x.com/i/user/<id>` works after renames. Snowflake timestamps: `(id >> 22) + 1288834974657` = Unix ms.
- **Image analysis:** Google Lens (crop to region of interest), TinEye, Yandex (faces). Twitter strips EXIF.
- **Geolocation:** Railroad signs, infrastructure maps (OpenRailwayMap), process of elimination.
- **Google Dorking:** `site:example.com filetype:pdf`, `intitle:"index of" password`. Append `&tbs=itp:face` for face-only image search.
- **DNS:** Always check TXT, CNAME, MX records for CTF domains.
- **Username OSINT:** whatsmyname.app (741+ sites), namechk.com.

## Resources

- **Shodan** - Internet-connected devices
- **Censys** - Certificate and host search
- **VirusTotal** - File/URL reputation
- **WHOIS** - Domain registration
- **Wayback Machine** - Historical snapshots
