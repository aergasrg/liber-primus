---
id: B11
title: Self-keyed book codes (page/line/sentence-indexed)
status: open
claimed_by: ""
rank: 11
ledger: [E0026]
---

# B11 Self-keyed book codes (page/line/sentence-indexed)

## Why
Fable 5.1 cracked Urquhart's 1653 ciphers with a self-keyed book code: number k indexes a word in section or page k of the same book. LP prints numbers (grid, page-15 square, numbered list, lone 7, solved magic squares); global-index and running-sum variants are negative (E0026), page-, line- and sentence-indexed variants are open.

## Test design
1. Inventory every number LP prints (grid, page-15 square, numbered list 1-5 in p33-39, the lone 7 in p8-14,
   magic squares on solved pages, cuneiform 1033/3301).
2. Indexing schemes: number pairs (unit, word-in-unit) with unit = page, line, sentence or section; first and
   last letters; 0- and 1-based. Use line counts or page images for pages (blank lines are unreliable).
3. Also derive rune keys the same way and apply them as running keys.
4. Detector: English bigram gain; control: planted book code under each scheme; null: random numbers through
   the same mapping. Count total readings for multiple testing.
5. Read the 2016 hint ('words are the map, numbers the direction') this way.
