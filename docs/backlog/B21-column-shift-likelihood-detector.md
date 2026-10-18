---
id: B21
title: Column-shift likelihood detector to extend E0027's power to longer page-local periods
status: claimed
claimed_by: claude/eloquent-hopper-k6fff6
rank: 4
ledger: [E0027]
---

# B21 Column-shift likelihood detector for page-local periodic keys

## Why
E0027 (B18) is lab-verified negative only for a single-page key of period 3 on pages of >= 217 runes.
At L >= 8 or on pages of <= 137 runes the column IoC detector cannot beat the multiplicity of the whole
search (55 pages x 4 views x ~135 periods x up to 4096 skip masks): L 8 on 273 runes reached at most
92/100, L 13 at most 57/100. IoC throws away letter identity. In the raw view a column is shifted
English mod 29; in the chain-unit view u = (p % 28 + k) % 28, so a column is shifted English mod 28 too.
Scoring each column by its best-shift English log-likelihood (lp.detectors unigram model, with the
mod-28 merge of F and EA in the chain view) uses letter identities and should carry far more power per
column of 5-30 symbols.

## Test design
1. Reuse E0027's views, page map, skip-mask machinery and surrogate generator (import, don't copy).
2. Detector per (page, view, L, mask): sum over columns of max over 28/29 shifts of the column's unigram
   LLR; standardise per (page, view, L) against the surrogates. Optionally add bigram gain across adjacent
   columns once shifts are fixed.
3. Tier 1 at the same conditions as E0027 (results/E0027/combined.txt) so the verified region can be
   compared directly; report the new region exactly.
4. Tier 2: 999 surrogate corpora with the whole search; hit = p <= 0.01, then the skeptic.

## Notes
Cost: 28-29 shifts x L columns per period; precompute per-column symbol counts, so a mask only changes
which column each segment's counts land in (same segment-pair trick does not apply directly; use
per-segment column count matrices rolled by the drift). Budget the skip pass the same way as E0027.
