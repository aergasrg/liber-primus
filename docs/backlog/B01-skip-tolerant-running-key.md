---
id: B01
title: Skip-tolerant running-key engine
status: open
claimed_by: ""
rank: 1
ledger: [E0008, E0012, E0024]
---

# B01 Skip-tolerant running-key engine

## Why
Every keyed solved section uses F-skips (a ciphertext F that passes through without consuming key). Every running-key scan in the ledger used rigid alignment, so a single skip early in a window destroys the match. Text and file running keys are therefore not actually excluded.

## Test design
1. Build `lp/runningkey.py`: score a ciphertext window against a key source while allowing the key offset to
   drift by one at each candidate F-skip (each ciphertext F). Either dynamic programming over drift
   (state = key offset delta, transitions only at ciphertext F positions, score = English unigram or bigram
   LLR) or short windows (e.g. 40-60 runes) at every position, chained by offset continuity.
2. Positive control: plant a running key from a known text into solved plaintext WITH F-skips at the solved-page
   rate (lp.controls.PlantRaw with FSkipEvery), confirm rigid FFT fails and the new engine recovers the offset.
3. Null: same engine with a shuffled or unrelated key text; record the best-of-offsets ceiling.
4. Re-run every text and file source already in the ledger (E0008 texts, E0012 bytes, E0024 files), raw form
   with LLR; chain form with IoC only.

## Notes
Skips in chain form: a skip is a ciphertext F whose step is not keyed; model it as a drift as well.
