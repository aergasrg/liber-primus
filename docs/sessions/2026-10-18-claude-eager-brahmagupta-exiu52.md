# 2026-10-18 claude/eager-brahmagupta-exiu52

Item: B18 Rerun E0002 in the step domain, page by page, with bounded F-skips  |  Status: done
Ledger: E0027

## What I did
- **Page map (B18 step 1, needed by B01/B12/B19)**:
  - `lp.data.PageLines` gives the lines on every LP page 0-55. I matched relikd's blank-line blocks to
    text-line counts on relikd's page images (`pages/pN.jpg` on raw.githubusercontent) and checked
    p3, p7, p33, p34, p38 and p39 by eye.
  - Blank lines mark paragraphs as well as pages: p3 = 6+5 lines, p7 = 9+1, p15 = 5+7 (digit square
    first), p33 = 5+6, p39 = 6+6. Page 50 is digits only.
  - `PageId`/`PosInPage` now follow real pages. `PageNumber` and `BlockId` are new, and `Pages(Section)`
    groups runes by page. The gate pins runes per page (18 tests).
- **lp-experiment skill**: the two-tier null rule the human asked for.
  - Negatives need >= 95/100 plants at the threshold, else "not identifiable at this length".
  - Hits need the whole search on 999 surrogates (or say how many) at p <= 0.01, then the skeptic.
- **lp-data**: its page-break pitfall is updated.
- **E0027**: four views (raw29, step29, unit28 with a doublet consuming / not consuming key) on 55
  pages, plus section-wide (L <= 300) and shared-period statistics.
  - Fs and F-adjacent steps are left out of the columns, so both chain F conventions shift the phase
    identically.
  - A segment-pair table scores each of up to 4096 skip masks with one lookup.
  - 999 step-permutation surrogates per run; tier 1 has 261 conditions x 100 plants per run.
- Run A used q = each page's own coincidence rate. Its tier 1 showed that a short periodic key raises
  the page's own IoC and hides itself, so run B uses q = 1/M. Per the human, A and B are two looks at
  the data with a x2 correction, and the power threshold is the stricter one (1 - 0.005/3).

## Results (control / null / best)
- Real data is null everywhere. Family-wise p is 0.259 (A) and 0.765 (B), so 0.518 with the x2
  correction. Best page: p13 step29 L 2 with 4 skips, 2.76 surrogate sd, explained by the doublet deficit
  in the step29 view (see the ledger notes).
- **Lab-verified negative region (x2-corrected, >= 95/100)**:
  - Single-page key, L 3:
    - 273 runes: all 3 models x 3 skip masks.
    - 217 runes: 7 of 9 conditions; the 2 misses (chain transparent-F, no or random skips) scored 94/100.
  - Section-wide key, no skips: L 7 on 308 and 1145 runes; L 60 on 1145 runes; L 250 raw on 1145
    runes (run A only).
  - One period shared by all pages: L 5, 20 and 60 (raw and chain).
- **Not identifiable**: single-page keys at L >= 8 (best 92/100), any page of <= 137 runes, section
  keys at L 60 on 308 runes. Full table: results/E0027/combined.txt and */summary.txt.

## Next steps (most useful first)
- B01 skip-tolerant running-key engine, now with real page boundaries (`Pages()`, `PosInPage`).
- B12 doublet event process (the page map is ready). B19 PRNG page-local: reuse E0027's skip-mask
  segment trick and surrogate generator.
- B21 (new): best-shift English likelihood per column, to push E0027's verified region past L 3.

## Do not repeat
- Column-IoC periodicity per page/section with these views (E0027): nothing more to learn from IoC.
  Extend power with B21 instead.
- Page map derivation: done and pinned in the gate.

## Needs a human
- Nothing. relikd's page images are reachable (raw.githubusercontent.com); api.github.com listing of
  other repos is blocked by the session's GitHub scope, which did not matter here.
