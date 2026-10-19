# 2026-10-19 claude/charming-babbage-raidxt

Item: B03 Public-domain Cicada texts as running keys (plus two chores requested in the prompt)  |  Status: done
Ledger: E0033, E0034, E0035

## What I did
- Claimed B03, gate passed (27 tests). The prompt also asked for two small chores, done in the same session.
- E0033: imported `gpu/results_E0029_gpu.json` with E0029 `import-gpu` and `report` (761.MP3, _560.00, 560.17,
  75 LP images). E0029 is append-only, so the result is a new entry; results/E0029/summary.* now cover 11 sources.
- E0034: recorded the 18 Oct Playground hunt (gpt-6-astra, outside the lab) as one entry (A-D) plus its
  iid-step indistinguishability proof. Not rerun here.
- E0035 (B03): `experiments/E0035_cicada_public_domain_texts.py` reuses the E0029 engine/null/power code via
  import and adds three sources; `scripts/fetch_keysources.sh` now fetches them.

## Results (control / null / best)
- E0033: GPU controls 8/8 recovered; best standardised lp_images 7.30, mp3_761 6.17, c560_00 5.80, c560_17 4.20
  against 11.01; null reps only 10/10/10/6. Negative.
- E0034: external, negative; its own planted control L=97 at 2.01; counts for B-D not recomputed here.
- E0035: best 5.14 (Liber AL p40), 5.21 (Britannica p1), 5.02 (Blake p53) against 9.71; planted controls
  100/100 at >= 141 runes. Negative.

## Next steps (most useful first)
- Fix `lp.runningkey.Trace` (StopIteration on unit28z2 plants; scores unaffected).
- Recompute E0034 B/C/D counts inside the lab if they will be cited (two-rune words, prime sums, F rate).
- B22 (six short pages) is still the only identifiability hole of the running-key family.

## Do not repeat
- Page-local running keys from any of the 14 sources now ledgered (E0029, E0033, E0035) in these 32 forms.

## Needs a human
- Nothing. (Optionally rerun the GPU null with 20 reps; no source is near the threshold.)
