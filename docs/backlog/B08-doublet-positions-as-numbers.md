---
id: B08
title: The 86 doublet positions read as numbers
status: open
claimed_by: ""
rank: 8
ledger: [E0025]
---

# B08 The 86 doublet positions read as numbers

## Why
Doublets are the only non-uniform feature. Their gaps, rune values and page positions may encode something.

## Test design
1. Extract the 86 positions (corpus index, section, word, page/line) and their rune values.
2. Read gaps, values and positions mod 29 as runes, as primes, as base-60 pairs; test against English and
   sequences.
3. Null: 86 random positions with the same per-section counts (permutation).

## Notes
Watch multiple testing: count every reading tried.
