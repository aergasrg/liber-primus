---
id: B04
title: Section titles as cribs
status: done
claimed_by: claude/clever-cori-kgjv4w
rank: 4
ledger: [E0010, E0036]
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

## Outcome
E0036 (2026-10-19, claude/clever-cori-kgjv4w): all 7 titles decrypted by every key window of 10 bounded
families and the full OEIS (first 100 terms, both directions), 6 additive forms, every F-skip subset.
Control and power 100/100; the only hits are on the 9-rune p15-22 title, at the chance level of a
50-replicate random-title null (p 0.57 / 0.53), and none reads on as English into the body. Negative.
