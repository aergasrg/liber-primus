# 2026-10-18 claude/eloquent-hopper-k6fff6

Item: B21 Column-shift likelihood detector to extend E0027's power to longer page-local periods  |  Status: done
Ledger: E0029

## What I did
- `experiments/E0029_column_shift_llr_pages.py` imports E0027's views, skip masks, surrogate generator
  and plants. Only the detector is new:
  - Each column is scored by its best-of-28/29-shift English unigram LLR. In the chain view, F and EA are
    merged as p mod 28.
  - Columns are pooled into a page z through a uniform-symbol Monte Carlo table of the mean and variance.
- Skip masks are searched at every period and view, where E0027 used only 8 candidate periods.
  - Speed trick: column scores are linear in the counts, so per-segment rolled count tensors are
    multiplied by the shift matrix once, before the mask gather.
  - Cost: 16.5 s per corpus, single thread.
- Search: L 2..min(20, n // 3), views raw29, unit28z1 and unit28z2 (step29 dropped; reason in the ledger).
  It uses one statistic, S1, at level 0.01.
- Runs: real data, 999 surrogates (resumed from a 210-surrogate checkpoint after a container restart) and
  288 tier-1 conditions x 100 plants.
- Renumbered E0028 -> E0029, because B12 merged E0028 to main while this ran. The plant seed label stays
  "E0028" in the script so the recorded plants reproduce.

## Results (control / null / best)
- Null: S1 threshold 4.17 (0.99 quantile of 999 surrogates). Real S1 3.14, p 0.153, so the real data is
  null and nothing went to the skeptic.
  - Best page: p55 L 13. It is a 76-rune page, so each of the 13 columns has ~5 symbols, and the unigram
    fit drifts to frequent letters with no words.
- **Lab-verified region (>= 95/100)**, all 3 models x 3 skip masks unless stated:
  - 273 runes: L 3-20, except chain literal-F with random skips at L 20 (94/100).
  - 217 runes: L 3-13, the DIVINITY and CIRCUMFERENCE lengths included. L 16 holds in 4 of 9
    conditions; L 20 holds raw with no skips only.
  - 137 runes: L 3-5. L 8 holds in 6 of 9 conditions; L 10 holds raw with no or random skips only.
  - 76 runes: raw L 3 only.
- E0027 had L 3 on >= 217 runes only. 42 of the 55 pages (85% of the runes) are >= 217 runes, though
  plants were run on the p3 and p25 layouts only.

## Next steps (most useful first)
- B22 (new): bigram-refined column shifts, to reach L 14-40 on long pages and L 5-20 on the 13 pages of
  < 217 runes.
- B01 skip-tolerant running-key engine (still rank 1). B19 PRNG page-local: E0029's rolled-count mask
  trick also works for any per-column score that is linear in counts.

## Do not repeat
- Unigram best-shift periodicity per page at L 2-20 with these views and masks (E0029). Inside the
  region above it is excluded; outside it, extend with B22, not by rerunning E0029.

## Needs a human
- Nothing.
