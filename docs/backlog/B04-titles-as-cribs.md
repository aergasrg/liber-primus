---
id: B04
title: Section titles as cribs
status: open
claimed_by: ""
rank: 4
ledger: [E0010]
---

# B04 Section titles as cribs

## Why
Solved sections open with short titles ending in the heading mark. p54-55 starts with a one-rune word 'A' plus 8 runes. Deriving key fragments from plausible titles and searching key sources for them is a cheap, high-yield crib.

## Test design
1. List the heading-terminated first words of every unsolved section (lp.data gives sentence ids; the
   heading mark is '⁜').
2. Build plausible title lists (Cicada vocabulary, solved titles' style: 'A WARNING', 'AN END', 'SOME WISDOM').
3. For each, derive raw keys (c - p) and chain units, then search key sources (sequences, texts, primes,
   LP plaintext) for those fragments, allowing F-skips.
4. Control: take a solved section, encrypt with a known source, check its true title's fragment is found.
5. Null: random titles of the same lengths.

## Notes
Design-heavy: suits Fable 5.1.
