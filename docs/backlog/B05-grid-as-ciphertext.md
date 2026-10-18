---
id: B05
title: The 256-byte grid as ciphertext
status: open
claimed_by: ""
rank: 5
ledger: [E0014, E0023]
---

# B05 The 256-byte grid as ciphertext

## Why
The base-60 grid decodes to 256 bytes with entropy 7.17 bits/byte spanning 0..255: it looks like ciphertext or a key, not text.

## Test design
1. Try it as raw OpenPGP packet data (look for packet tags, `gpg --list-packets`).
2. AES-128/256 (ECB/CBC, zero IV) with keys derived from LP words (MD5/SHA-256 of words), look for headers or
   printable output.
3. XOR with the page-56 hash, the 2013 cookies and 2013 files; check for headers (PNG, JPEG, gzip, PGP).
4. Control: encrypt a known header-bearing blob the same way and confirm the header detector fires.

## Notes
Grid first bytes cbe7a7ba61ed7eb7. Not an RSA modulus (divisible by 2, 5, 43, 53).
