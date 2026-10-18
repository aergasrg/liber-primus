---
id: B15
title: Deck and permutation-state keystreams (Solitaire-style)
status: open
claimed_by: ""
rank: 15
ledger: []
---

# B15 Deck and permutation-state keystreams (Solitaire-style)

## Why
A hand-operated deck cipher (Schneier's Solitaire/Pontifex, published 1999 in a novel Cicada's
circle would know) produces a flat, aperiodic keystream with no period and no depth, and is
executable with 28 numbered slips and the printed prime table. No state-machine cipher is in the
ledger (E0019-E0021 are PRNGs and hash pads). Council designer call, item 10
(docs/council/2026-10-18/03-gpt-6-astra-kickoff-designer.md).

## Test design
1. Generators: (a) Solitaire with a 28- and a 29-card deck, keyed by each of the 96 Cicada words used
   in E0021 and by DIVINITY, CIRCUMFERENCE, FIRFUMFERENFE; (b) the council's deck: distinct runes of
   DIVINITY first (23,10,1,9,16,26), the rest ascending, rotated by the section's first page number,
   then after each rune rotate by 1 + G(p) mod 28 and swap positions 0 and (c_i + j) mod 28.
2. Variant (a) is a pure keystream: scan as E0019 (IoC on the first 300 runes, raw and chain, both
   signs). Variant (b) is plaintext-reactive: sequential decode with LLR, branching at F-skips.
3. Control: plant each generator over solved plaintext and recover it. Null: E0019's extreme-value
   ceiling (1.20-1.25 on 300 runes) for (a); shuffled-deck decodes for (b).

## Notes
Low rank: no evidence points at decks, but the family is untested and cheap for (a).
