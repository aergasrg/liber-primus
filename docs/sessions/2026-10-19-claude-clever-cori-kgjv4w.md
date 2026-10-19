# 2026-10-19 claude/clever-cori-kgjv4w

Item: B04 Section titles as cribs  |  Status: done
Ledger: E0036

## What I did
- Claimed B04, gate passed (27 tests).
- Ported outside/CribTest.py and outside/ReverseCrib2.py (outside run, 19 Oct) into
  `experiments/E0036_title_cribs.py` on `lp/`; the outside counts reproduce exactly (p15-22 89 rows, others 0)
  and the planted 'A REMINDER' control is recovered.
- Extended it: F-skip subsets for the three titles with a ciphertext F (chain bridge/through modes), and the
  full OEIS (`scripts/fetch_keysources.sh` now fetches oeis.org/stripped.gz), first 100 terms, both directions.
- Tier-1 power (100 plants, both sources, 22 with skips), 50-replicate random-title null per title, and a
  continuation recheck reading each hit key on into the section body. `results/E0036/run_all.sh` resumes.

## Results (control / null / best)
- Control: A REMINDER recovered; power 100/100.
- p15-22: 365 (bounded) / 374 (OEIS) distinct chance titles vs null mean 373 / 393, p 0.57 / 0.53.
- Every other title: 0 hits (chance 0.0-0.4). Best continuation z 3.29 < Bonferroni 4.39. Negative.

## Next steps (most useful first)
- Key carried in from the previous section (window starting before the title) was not tried; cheap to add.
- Measure the power of the continuation recheck for short titles (p15-22, p54-55) where crib hits are not
  rare by themselves.
- Fix `lp.runningkey.Trace` (from the last session) is still open.

## Do not repeat
- Title cribs with these 10 bounded families or OEIS first-100-term windows, 6 additive forms, F-skips (E0036).

## Needs a human
- Nothing.
