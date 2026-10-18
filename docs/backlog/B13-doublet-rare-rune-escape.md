---
id: B13
title: Doublets as escapes for a set of rare plaintext runes
status: open
claimed_by: ""
rank: 13
ledger: [E0025]
---

# B13 Doublets as escapes for a set of rare plaintext runes

## Why
A chain cipher with a 28-step key cannot carry 29 plaintext symbols. The council's designer call
(docs/council/2026-10-18/03-gpt-6-astra-kickoff-designer.md, shared codec of items 1-9) proposes
that step 0 is an *escape*: it means "the plaintext rune is a rare one", with the rare rune either
fixed or selected by the key from a small set, and the 28 non-zero steps carry the other runes
after re-ranking. E0025 excluded a *single* rune mapped to step 0. A set of rare runes is open.
Measured (this session): the five rarest runes in the solved pages (EO 12, OE 22, AE 25, J 11, X 14)
total 0.34% (baseline corpus 0.37%); adding IA/IO 27 gives 0.87% (0.80%). Observed doublet rate
0.664%. No set fits exactly, so a key-selected subset or a plaintext with a different rare-rune mix
would be needed; that is the first thing to check.

## Test design
1. Profile test (no key): the position-in-word and word-length profile of the 86 doublets vs the
   profile of each candidate set S (the 4, 5, 6 rarest runes, with and without 27 and 28) in the solved
   pages and the baseline corpus. Chi-square with df from the bins; control = 86 positions sampled from
   the true S profile; null = 86 positions sampled from the all-rune profile (10^4 draws each).
2. Rate test: for each S, the expected escape count on 12,956 runes vs 86, with the Poisson interval.
3. Codec decode (needs a key source): under the codec, step s = 1 + (rank(p) + t) mod 28 with rank(p)
   the plaintext rune's index among the 28 non-escaped runes. Run the running-key scans of B01 with this
   codec in place of plain subtraction. Control: plant the codec over solved plaintext with a known key
   and recover it. Null: shuffled key.

## Notes
If the profile test rejects every S, doublets are not plaintext-driven and the key-gate view (B12)
stands.
