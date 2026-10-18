---
id: B01
title: Skip-tolerant running-key engine
status: claimed
claimed_by: claude/blissful-gates-2v36sv
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

## Council additions (2026-10-18, docs/council/2026-10-18/04-gpt-6-astra-kickoff-negatives.md, T2)
The audit of E0008 found four gaps; the engine must cover all of them or the rerun excludes nothing:
1. Alignment is page-local: search every source offset against every *page* (real page map, see B18),
   with an independent source and offset per page, 0-11 non-consuming F's per page, and no requirement
   that the recovered offset continue on the next page. With a unigram LLR the skip search is an exact
   dynamic program over the key index (cost about K x 12 x 12,956 per form, K = source positions);
   a rigid FFT shortlist followed by skip repair does not close the gap, because the true offset need
   not enter the shortlist. About 60-68% of a 300-rune window must stay aligned for the LLR to exceed
   zero, so one skip after 100 runes leaves -0.27 to -0.43 per rune.
2. Representation: apply the source to the raw runes mod 29, to the steps mod 29, and to the non-zero
   steps u = s - 1 mod 28 (both zero-step conventions: a zero does / does not consume a key symbol).
3. Tokenisation: an English source has several rune spellings (TH, NG, EA, OE, AE, IA/IO, EO as one
   rune or as letters). Build a lattice that allows each digraph either way per occurrence and search
   it jointly with the skip alignment; keep the lattice identical in the null. Reverse rune-token
   sequences, not Latin characters, for reversed keys.
4. Polarity: p = a c + b k with a, b in {-1, +1} in the declared domain (eight direction/polarity
   forms); c - k and c + k alone are not all polarities.
Plants must carry the features: irregular masks with a first skip before rune 50, near 100 and late;
adjacent pages from different offsets; mixed tokenisation inside one passage; a reversed Beaufort
source. Null: the whole optimised search on 999 surrogate corpora (non-zero steps permuted within
pages, zeros kept, re-integrated, F positions recomputed); hit = max-search p <= 0.01, confirmed by a
frozen-key continuation. Not worth doing: more rigid whole-section scans; a huge new corpus before the
engine passes these plants; non-English scoring as the first repair.
