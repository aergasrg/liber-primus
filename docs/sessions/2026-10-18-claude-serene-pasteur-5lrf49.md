# 2026-10-18 claude/serene-pasteur-5lrf49

Item: B12 Structure of the doublet event process  |  Status: done
Ledger: E0028

## What I did
- `experiments/E0028_doublet_event_process.py` computes 18 corpus-level statistics of the 86 doublet
  positions:
  - spacing: gap KS, min gap, gap CV;
  - lag 1..20 pair counts;
  - same-word pairs;
  - packets of 16/29/32 and printed lines;
  - Fano factor;
  - three periodicity searches over L 2..300;
  - doublet-rune chi2;
  - line, page and word-break counts.

  Per-section counts are tested separately. The null is 10^5 within-section permutations, and the
  family-wise p is the min-p over the 18. The run takes about 2 minutes and checkpoints per chunk.
- Tier 1: 46 planted conditions × 100 synthetic chain ciphertexts. Doublets are re-extracted from the
  runes by the same function as the real run.
- Deterministic strict-rule checks (`strict_rules.txt`).
- Step-7 recheck of the best period on the non-zero steps and the raw runes, with planted period keys
  as controls (`top_period_recheck.txt`).
- The 18 Oct preliminary chat result is confirmed with lab nulls. Its L 215 signal is the corpus-wide
  collision form, which my first two period statistics missed. I added it as PeriodColl, so its p is post hoc.
- B02 now has a "Target from B12" section.

## Results (control / null / best)
- Calibration: uniform plants 1/100 recovered at family p <= 0.01.
- Real data: family-wise p 0.090; per-section counts p 0.63. Verdict: memoryless.
- Best single statistic: PeriodColl at L 215, z 5.80 (p 0.0086 alone). 37 of its 40 pairs cross a
  section break. In the recheck, L 215 shows z -0.10 in the steps and 0.39 in the raw runes, against
  11-95 for planted keys. Not a hit.
- Lab-verified exclusions (>= 95/100):
  - refractory R >= 15;
  - on/off regimes with stay >= 0.95;
  - one per 29 or 32 packet;
  - strong periodic gates (see ledger);
  - doublets confined to 10% of words;
  - line-start fraction 0.2, page-start 0.1.
- Excluded by logic: strict refractory R >= 7 (min gap 6), one per line, one per P-packet for
  P >= 15 (section-aligned) or P >= 19 (page-aligned).
- Not identifiable with 86 events: rune preference (45/100 even at ×3 on 7 runes), word-start
  preference, section-rate differences (89/100 at sigma 0.8), refractory R <= 10, and short regimes.

## Next steps (most useful first)
- B02 with the new target: a repeat-avoiding rule that leaks at 0.19 of the random rate, memoryless, and
  at most a 6-position refractory window.
- B13: the rune-preference test here is weak, so B13 must bring its own plaintext-side power, not lean
  on E0028's RuneChi2.
- B08 is not downgraded. Numbers encoded in positions would look uniform to every statistic here.

## Do not repeat
- Placement statistics of the 86 doublets (E0028), including period L 2..300 in all three forms. Do not
  chase L 215.

## Needs a human
- Nothing.
