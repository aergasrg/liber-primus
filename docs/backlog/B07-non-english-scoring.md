---
id: B07
title: Non-English plaintext scoring
status: open
claimed_by: ""
rank: 7
ledger: []
---

# B07 Non-English plaintext scoring

## Why
All detectors assume English. Latin, Old English or number-heavy 'Runeglish' would score low on English LLR while still being plaintext.

## Test design
1. Build unigram/bigram models in runes for Latin, Old English and a numerals-spelled-out English.
2. Re-score the top candidates kept by previous runs (results files) under each model.
3. Control: plant Latin plaintext and confirm the Latin model separates it from noise while English does not.

## Notes
Cheap if earlier runs kept top-N candidate lists.
