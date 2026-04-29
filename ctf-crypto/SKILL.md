---
name: ctf-crypto
description: Provides cryptography attack techniques for CTF challenges. Use when attacking encryption, hashing, signatures, ZKP, PRNG, or mathematical crypto problems involving RSA, AES, ECC, lattices, LWE, CVP, number theory, Coppersmith, Pollard, Wiener, padding oracle, GCM, key derivation, or stream/block cipher weaknesses.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Cryptography

## Additional Resources

- [classic-ciphers.md](references/classic-ciphers.md) - Classic ciphers: Vigenere (+ Kasiski examination), Atbash, substitution, XOR variants, OTP key reuse / many-time pad, homophonic substitution, grid permutation, XOR key recovery via file format headers
- [modern-ciphers.md](references/modern-ciphers.md) - Modern cipher attacks: AES (CFB-8, ECB leakage), CBC-MAC/OFB-MAC, padding oracle, S-box collisions, GF(2) elimination, AES-GCM nonce reuse (forbidden attack), Bleichenbacher RSA PKCS#1 v1.5 oracle, birthday attack / meet-in-the-middle, CRC32 collision forgery
- [modern-ciphers-2.md](references/modern-ciphers-2.md) - Modern cipher attacks part 2: Blum-Goldwasser bit-extension, hash length extension, compression oracle, OFB invertible RNG, HMAC-CRC linearity, DES weak keys, square attack, PBKDF2 pre-hash bypass, MD5 multi-collision
- [modern-ciphers-3.md](references/modern-ciphers-3.md) - Modern cipher attacks part 3: custom hash state reversal, CBC IV forgery + block truncation, padding oracle to CBC bitflip RCE, SPN S-box intersection, AES-CBC error-message oracle, HMAC key recovery
- [stream-ciphers.md](references/stream-ciphers.md) - Stream ciphers: LFSR (Berlekamp-Massey, correlation attack, known-plaintext, Galois vs Fibonacci, Galois tap recovery via autocorrelation), RC4 second-byte bias, XOR consecutive byte correlation
- [rsa-attacks.md](references/rsa-attacks.md) - RSA attacks: small e (cube root), common modulus, Wiener's, Pollard's p-1, Hastad's broadcast, Hastad with linear padding (Coppersmith), Franklin-Reiter, Coppersmith linearly-related primes, Fermat/consecutive primes, multi-prime, restricted-digit, Manger oracle
- [rsa-attacks-2.md](references/rsa-attacks-2.md) - RSA attacks part 2: RSA p=q validation bypass, cube root CRT, multiplicative homomorphism forgery, weak keygen via base representation, RSA-CRT fault attack, homomorphic decryption bypass, RSA signature bypass with e=1
- [ecc-attacks.md](references/ecc-attacks.md) - ECC attacks: small subgroup, invalid curve, Smart's attack (anomalous, with Sage code), fault injection, clock group DLP, Pohlig-Hellman, ECDSA nonce reuse, Ed25519 torsion side channel, DSA nonce reuse, DSA key recovery via MD5 collision
- [zkp-and-advanced.md](references/zkp-and-advanced.md) - ZKP/graph 3-coloring, Z3 solver guide, garbled circuits, Shamir SSS, race conditions, Groth16 broken setup, DV-SNARG forgery, KZG pairing oracle
- [prng.md](references/prng.md) - PRNG attacks (foundational): MT19937, MT float recovery via GF(2), LCG, V8 XorShift128+ state recovery via Z3, middle-square, time-based seeds, C srand/rand via ctypes, logistic map chaotic PRNG
- [prng-attacks.md](references/prng-attacks.md) - PRNG attacks (CTF-era): MT subset-sum seed recovery, Rule 86 cellular automaton reversal via Z3, Java LCG meet-in-the-middle, LFSR bit-fold ASCII parity, Z3 solve-time timing oracle, randcrack DSA k prediction, NTP-poisoned PRNG UUID XOR
- [historical.md](references/historical.md) - Historical ciphers (Lorenz SZ40/42, book cipher implementation)
- [advanced-math.md](references/advanced-math.md) - Advanced mathematical attacks: isogenies, Pohlig-Hellman, baby-step giant-step (BSGS), LLL, Merkle-Hellman knapsack via LLL, Coppersmith, quaternion RSA, GF(2)[x] CRT, S-box collision, LWE lattice CVP attack, introspective CRC via GF(2) linear algebra
- [lattice-and-lwe.md](references/lattice-and-lwe.md) - Lattice attack triage and workflow: LLL/BKZ/Babai, HNP from partial or biased nonces, truncated LCG state recovery, LWE embedding and CVP, Ring-LWE / Module-LWE recognition, orthogonal lattices, subset sum / knapsack
- [exotic-crypto.md](references/exotic-crypto.md) - Exotic algebraic structures: braid group DH / Alexander polynomial, monotone function inversion, tropical semiring residuation, Paillier, Hamming code interleaving, ElGamal universal re-encryption, FPE Feistel brute-force
- [exotic-crypto-2.md](references/exotic-crypto-2.md) - Exotic algebraic structures part 2: BB-84 QKD MITM, ElGamal trivial DLP, Paillier LSB oracle, Goldwasser-Micali replication oracle, homomorphic encryption bit-extraction, ElGamal over matrices, OSS signature forgery

## When to Pivot

- If the real blocker is understanding a binary, obfuscated client, or weird VM, switch to `/ctf-reverse`.
- If the challenge is mostly packet carving, disk recovery, or stego extraction before any decryption starts, switch to `/ctf-forensics`.
- If the task is just implementing an exploit against a vulnerable network service after the crypto part is solved, switch to `/ctf-pwn` or `/ctf-web`.
- If the crypto challenge involves adversarial ML, model extraction, or neural-network-based ciphers, switch to `/ctf-ai-ml`.
- If the challenge is really an encoding puzzle, esoteric cipher, or polyglot trick rather than true cryptanalysis, switch to `/ctf-misc`.

## Quick Lattice / LWE Triage

If the challenge gives modular linear equations plus a promise that the hidden quantity is small, sparse, biased, or only partially leaked, treat it as a lattice candidate first. Start with LLL, move to BKZ when LLL almost works, and use Babai for approximate CVP. See [lattice-and-lwe.md](references/lattice-and-lwe.md) for full attack selection and failure-mode triage.

## Quick Start Commands

```bash
# Identify cipher type / size
python3 -c "from Crypto.Util.number import *; n=<N>; print(f'bits={n.bit_length()}')"

# RSA quick check
python3 -c "from sympy import factorint; print(factorint(<n>))"  # Small factors?
openssl rsa -pubin -in key.pub -text -noout  # Extract n, e from PEM

# Quick factorization
python3 RsaCtfTool.py -n <n> -e <e> --uncipher <c>

# XOR analysis
python3 -c "from pwn import xor; print(xor(bytes.fromhex('<hex>'), b'flag{'))"

# Hash identification
hashid '<hash>'
hashcat --identify '<hash>'

# SageMath (for lattice/ECC)
sage -c "print(factor(<n>))"
```

## Useful Tools

- **Python:** `pip install pycryptodome z3-solver sympy gmpy2`
- **SageMath:** `sage -python script.py` (required for ECC, Coppersmith, lattice attacks)
- **RsaCtfTool:** `python RsaCtfTool.py -n <n> -e <e> --uncipher <c>` — automated RSA attack suite
- **quipqiup.com:** Automated substitution cipher solver (frequency + word pattern analysis)
