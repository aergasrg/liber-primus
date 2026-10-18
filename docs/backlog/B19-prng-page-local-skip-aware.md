---
id: B19
title: Rerun E0019/E0020 page-locally, skip-aware, with reduction wrappers
status: open
claimed_by: ""
rank: 4
ledger: [E0019, E0020]
---

# B19 Rerun E0019/E0020 page-locally, skip-aware, with reduction wrappers

## Why
The PRNG sweeps scored the first 300 runes of each *section* at a rigid alignment with no skips, no
burn-in and no origin offset, and their plant had none of those features either. The council audit
(docs/council/2026-10-18/04-gpt-6-astra-kickoff-negatives.md, T3 gaps 1, 2, 4) quantifies the loss:
with m aligned runes in 300 the expected IoC is about 1 + 0.78 m(m-1)/(300 x 299), so a first skip
after 100 runes gives 1.09 and after 150 gives 1.19, both under the 1.20-1.25 ceiling; 163 correct
runes out of 300 give 1.23, which is exactly the "best 1.23, then 1.01 on the whole section" that
E0019 reported, so that fall is also what a correct first-page key followed by a page change looks
like. A draw-reject wrapper (draw 0..28, reject 28) also gives a flat 28-symbol key but a different
stream from rand % 28, with no rejection-free run of 300 draws (p = 2.7e-5).

## Test design
1. Same generators and seed sets as E0019/E0020 (drand48, glibc, Python 2 and 3 recipes), plus two
   wrappers around each 29-valued stream: reject 28 and keep 0-27; reject 0 and keep 1-28 minus one.
2. Score within each *page* (real page map from B18 step 1), aligned at every page start, four forms
   (raw +-, chain +-), both zero-step conventions (zero consumes a key symbol or not).
3. Skips: 0-11 non-consuming F's per page. Optimise an additive unigram LLR by dynamic programming
   over the key index (exact for LLR; IoC is reported on the recovered candidate, not optimised),
   both chain conventions for a skipped F.
4. Origin and burn-in box, on the 22 named Cicada seeds only: ciphertext origin 0-63 within each
   page (keep starts with >= 120 runes), burn-in 0-1023.
5. Positive controls (each must be recovered in >= 95 of 100 plants): 1, 2 and 11 irregular skips
   per page with an early one; advancing and non-advancing zero events; glibc and both Python recipes,
   not only drand48; independent seeds on adjacent pages; a non-zero origin; burn-ins 37 and 1023.
6. Null: the full adaptive search on 999 surrogate corpora (B18 step 6); hit = max-search p <= 0.01,
   then a continuation on the rest of the page under the frozen key.

## Notes
Cost: page-start coverage about 1.4e11 symbol visits before skip states (vectorise with numpy as
in PrngSweep.py; run in the background with checkpoints). The origin/burn-in box is 64 x 1024 larger
and is therefore restricted to the named seeds. Not worth doing: a Cartesian product of all seeds x
origins x burn-ins x skips; more raw mod-29 sweeps (a uniform pad predicts 446 doublets); a fixed
1.25 cutoff after widening the search.
