---
id: B18
title: Rerun E0002 in the step domain, page by page, with bounded F-skips
status: claimed
claimed_by: claude/eager-brahmagupta-exiu52
rank: 3
ledger: [E0002]
---

# B18 Rerun E0002 in the step domain, page by page, with bounded F-skips

## Why
E0002 (external, no control, no null) tested periodic keys on the raw runes of whole sections. The
council audit (docs/council/2026-10-18/04-gpt-6-astra-kickoff-negatives.md, T1 gaps 1-3) shows three
ways a real periodic key would have been missed: (1) a periodic key applied to the steps
u_i = s_i - 1 mod 28 (the chain form that fits the fingerprint) leaves the raw-rune columns flat,
because the running sum mixes key and plaintext history; (2) the solved keys change per page, and a
section column that mixes four independent page keys has a column IoC near 1.19, six near 1.13; (3) one
missed F-skip shifts every later column assignment, and r phase groups give IoC about 1 + 0.78/r.
Every keyed solved page has F-skips, so a raw, section-wide, fixed-skip scan is the wrong test.

## Test design
1. Page map first: real page boundaries for all 56 pages (E0015 noted blank-line breaks are wrong for
   p3-7, p15-22, p33-39, p40-53; use line counts or the page images). Record it in `lp.data`.
2. Three views per page: raw c_i mod 29; steps s_i mod 29; u_i = s_i - 1 mod 28 over non-zero steps,
   with both zero-step conventions (zero consumes a key symbol / does not). Periods 1-300 per page
   and per section. Omit the first edge of each page.
3. Detector: pair-weighted column IoC, standardised per (window length, period) against the null.
4. F-skips: enumerate subsets of a page's ciphertext F's with 0-11 skips (cost 300 x L x sum of
   binomials; cap at 2^12 subsets per page and say so). Two chain conventions for a skipped F:
   literal F becomes the chain state, or the F is transparent and steps are recomputed between
   retained runes.
5. Positive control: integrated periodic chains planted over solved plaintext poured into real page
   layouts, with independent keys on adjacent pages, periods short, mid and near page length, irregular
   skip masks including the Welcome pattern, and both zero conventions. Report power by page length
   and period; where plants are not recovered say "not identifiable at this length", not "excluded".
6. Null: 999 surrogate corpora made by permuting the non-zero steps within each page (zero positions,
   boundaries and lengths kept), re-integrated from random page-initial runes, with F positions
   recomputed; run the whole search on each; hit = max-search p <= 0.01.

## Notes
Cost before skips: 3 views x 300 periods x 12,956 = 1.2e7 symbol visits; trivial. The skip subsets
dominate; run them for the top periods only after the no-skip pass, and say so in the ledger.
Not worth doing (per the audit): Beaufort as a separate IoC test (reflection preserves IoC), initial
phase variants, periods beyond the page length, arbitrary interrupter runes (E0003 overfits).
