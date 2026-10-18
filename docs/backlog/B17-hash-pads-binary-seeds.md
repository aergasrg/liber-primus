---
id: B17
title: Hash pads from binary leads with section labels
status: open
claimed_by: ""
rank: 17
ledger: [E0021]
---

# B17 Hash pads from binary leads with section labels

## Why
E0021 seeded 4,032 hash pads from 96 Cicada *words*. The binary leads were not seeds: the page-56
hash bytes, the 256 grid bytes, the two 2013 cookies, the 2012 factors. Both council kickoff calls
(docs/council/2026-10-18/02-gpt-6-astra-kickoff-cryptanalyst.md items 1, 2, 6, 7;
03-gpt-6-astra-kickoff-designer.md item 12) proposed exactly these seeds with a per-section label
and a counter, reduced with rejection sampling. A small, bounded extension of E0021.

## Test design
1. Seeds: page-56 hash (64 bytes), grid (256 bytes), cookies 167 and 761 (32 bytes each), P, Q and
   their product (big-endian bytes), ASCII "1033", "3301", "LP". Expansions: SHA-512 and BLAKE2b
   of seed || label || counter (labels: none, section name, first page number as one byte), HMAC
   with the same; reduction: byte mod 29 / 28 with rejection (bytes >= 232 / 224 discarded), and
   base-29 digits of the digest.
2. Scan as E0021: first 300 runes of each section, four forms; IoC.
3. Control: one pad planted over solved plaintext and recovered. Null: E0019's extreme-value
   ceiling (1.20-1.25) at the trial count actually run.

## Notes
The cryptanalyst call's gate constructions (step 0 forced when a hash-derived value hits 0, with
P = 1/149 fitted to 86) are untestable without the seed and are not filed; their seed-free
predictions are B12.
