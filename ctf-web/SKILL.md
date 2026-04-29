---
name: ctf-web
description: Provides web exploitation techniques for CTF challenges. Use when the target is primarily an HTTP application, API, browser client, template engine, identity flow, or smart-contract frontend/backend surface, including XSS, SQLi, SSTI, SSRF, XXE, JWT, auth bypass, file upload, request smuggling, OAuth/OIDC, SAML, prototype pollution, and similar web bugs. Do not use it for native binary memory corruption, reverse engineering of standalone executables, disk or memory forensics, or pure cryptanalysis unless the web flaw is still the main path to the flag.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Web Exploitation

## Additional Resources

- [sql-injection.md](references/sql-injection.md) - SQL injection techniques: auth bypass, UNION extraction, filter bypasses, second-order SQLi, truncation, race-assisted leaks
- [server-side.md](references/server-side.md) - PHP type juggling, LFI, SSTI (Jinja2, Twig, ERB, Mako, EJS, Smarty), SSRF (Host header, DNS rebinding, curl redirect)
- [server-side-2.md](references/server-side-2.md) - XXE (basic, OOB, DOCX upload), XML injection, command injection, GraphQL injection
- [server-side-exec.md](references/server-side-exec.md) - Direct code execution paths, upload-to-RCE, deserialization-adjacent execution, LaTeX injection
- [server-side-exec-2.md](references/server-side-exec-2.md) - More execution chains: SQLi fragmentation, path parser tricks, polyglot uploads
- [server-side-deser.md](references/server-side-deser.md) - Java/Python/PHP deserialization and race-condition playbooks
- [server-side-advanced.md](references/server-side-advanced.md) - Advanced SSRF, traversal, archive, parser, and framework issues
- [server-side-advanced-2.md](references/server-side-advanced-2.md) - Docker API SSRF, Windows path tricks, rogue MySQL server file read
- [server-side-advanced-3.md](references/server-side-advanced-3.md) - WAV polyglot upload, SoapClient CRLF smuggling, gopher SSRF
- [server-side-advanced-4.md](references/server-side-advanced-4.md) - WeasyPrint SSRF (CVE-2024-28184), MongoDB regex oracle, React RSC RCE (CVE-2025-55182)
- [client-side.md](references/client-side.md) - XSS, CSRF, cache poisoning, DOM tricks, admin bot abuse, request smuggling
- [client-side-advanced.md](references/client-side-advanced.md) - CSP bypasses, Unicode tricks, XSSI, CSS exfiltration, browser normalization quirks
- [auth-and-access.md](references/auth-and-access.md) - Auth/authz bypasses, hidden endpoints, IDOR, redirect chains, subdomain takeover
- [auth-and-access-2.md](references/auth-and-access-2.md) - Unicode homograph username collision, SRP bypass, ArangoDB AQL MERGE privesc
- [auth-jwt.md](references/auth-jwt.md) - JWT/JWE manipulation, weak secrets, header injection, key confusion, replay
- [auth-infra.md](references/auth-infra.md) - OAuth/OIDC, SAML, CORS, CI/CD secrets, IdP abuse, login poisoning
- [node-and-prototype.md](references/node-and-prototype.md) - Prototype pollution, JS sandbox escape, Node.js attack chains
- [web3.md](references/web3.md) - Solidity and Web3 challenge notes
- [cves.md](references/cves.md) - CVE-driven techniques matched against challenge banners, headers, dependency leaks, or version strings
- [field-notes.md](references/field-notes.md) - Long-form exploit notes: quick references for all major web attack categories

## When to Pivot

- If the target is a native binary, custom VM, or firmware image, switch to `/ctf-reverse`.
- If the HTTP bug only gives you code execution and the hard part becomes memory corruption or seccomp escape, switch to `/ctf-pwn`.
- If the "web" challenge really turns on JWT math, custom MACs, or crypto primitives, switch to `/ctf-crypto`.
- If the challenge involves analyzing logs, PCAPs, or recovering artifacts from a web server, switch to `/ctf-forensics`.
- If the challenge requires gathering intelligence from public web sources, DNS records, or social media before exploitation, switch to `/ctf-osint`.

## First-Pass Workflow

1. Identify the real boundary: browser only, backend only, mixed app, or auth flow.
2. Capture one normal request/response pair for every major feature before fuzzing.
3. Enumerate hidden functionality from JS bundles, response headers, routes, and alternate methods.
4. Classify the likely bug family: injection, authz, parser mismatch, upload, trust proxy, state machine, or client-side execution.
5. Build the smallest proof first: leak, bypass, or primitive. Save full exploit chaining for later.

## Quick Start Commands

```bash
# Recon
curl -sI https://target.com
ffuf -u https://target.com/FUZZ -w wordlist.txt
curl -s https://target.com/robots.txt

# SQLi quick test
sqlmap -u "https://target.com/page?id=1" --batch --dbs

# JWT decode (no verification)
echo '<token>' | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# Cookie decode (Flask)
flask-unsign --decode --cookie '<cookie>'
flask-unsign --unsign --cookie '<cookie>' --wordlist rockyou.txt

# SSTI probes
curl "https://target.com/page?name={{7*7}}"
curl "https://target.com/page?name={{config}}"

# Request inspection
curl -v -X POST https://target.com/api -H "Content-Type: application/json" -d '{}'
```

## Common Flag Locations

- Files: `/flag.txt`, `/flag`, `/app/flag.txt`, `/home/*/flag*`
- Environment: `/proc/self/environ`, process command line, debug config dumps
- Database: tables named `flag`, `flags`, `secret`, or seeded challenge content
- HTTP: custom headers, archived responses, hidden routes, admin exports
- Browser: hidden DOM nodes, `data-*` attributes, inline state objects, source maps
