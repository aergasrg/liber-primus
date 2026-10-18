# 2026-10-18 claude/admiring-brown-6qihly

Item: B24 (F-run fix) and B25 (key-free leak-rule tests): two items, run in that order at the human's request  |  Status: done
Ledger: E0031, E0032

## What I did
- **B24, item 1.** `lp/runningkey.py` `PageEvents` now builds one event per F-run in the step views.
  - Each F of a run is keyed, a literal skip or a transparent skip.
  - `Trace` takes per-option skip labels and the plaintext order from `PageEvents(..., Labels=True)`.
  - The same fix is in `gpu/E0029_bytes_gpu.py`.
- **Tests.** Two new gate tests in `tests/test_gate.py`; both fail on the old code and pass on the new.
  - The B24 failing input.
  - A brute force over every keyed / literal / transparent F assignment.
  - Gate: 27 pass.
- **E0031.** Reran the step views on pages 9, 29, 32 and 36 for the 7 CPU sources, real source plus
  E0029's 20 null seeds, and merged the result into E0029's tables (see `results/E0031/summary.txt`).
- **CPU/GPU parity** (`E0031 parity`): exact match.
  - Events are identical on the 55 real pages and 2,000 random pages in all 4 views.
  - The GPU loaders give identical pages and English weights.
  - `Engine.Run` (PyTorch CPU) equals `RunEvents` on 3,520 runs, score difference 0, end pointer
    mismatches 0.
  - `--quick` also passed all 4 GPU-source controls on CPU.
- **E0032 (B25).** The 5 preregistered statistics were committed (331947d) before the real stage.
  - Positive controls: 7 control laws on the common core.
  - Nulls: 10^4 Markov corpora, 10^4 E0027 surrogates, 10^5 permutations.

## Results (control / null / best)
- **E0031: negative, and E0029 stands.** The FF pages reach at best z 2.85 (p29, lp_plain), at least 23
  score units below threshold.
  - Plants needing an F-run option, on the long FF pages: fixed engine 100/100, old engine 98-100/100,
    so the bug cost little power there.
  - Page 32 (121 runes): fixed 92-97, old 39-68. Still not identifiable (<= 140 runes).
- **E0032: negative.**
  - Lag-k coincidences R_2..R_10: 440, 439, 458, 477, 454, 448, 436, 461, 440. Null mean 445.8, sd 20.7.
    The z-scores run from -0.80 to +1.53, and the +1.53 is lag 5, slightly outside the outside note's
    +-1.5.
  - Stale register at lag 4: 0 of 1,000 rule plants reach R_4 = 458 (rule mean 357, sd 19), so it is
    excluded.
  - Preceding-step gate: p 0.74. Running-checksum gate: p 0.22. Both excluded, with 100/100 power.
  - Not identifiable: step band (3/100), guard renewal (2/100), word lanes (0.79 expected same-word pairs).
  - Family min-p 0.022 (T5a guard LR; no power behind it). Bonferroni 0.11.

## Next steps (most useful first)
- **Human: merge this PR before tonight's GPU run.** gpu/README.md downloads the script from `main`, and
  the fixed version is only on this branch until the merge.
- B26: the rest of B24 (plant doublet multiplicity, E0027 skip/doublet conflicts, hardening).
- B02 or B03: the ordinary key-source items. The leak-rule constructions with a key-free test are now
  spent.

## Do not repeat
- The FF-page step-view rerun (E0031) and the B25 statistics T1-T5 (E0032).
- Stale-register leaks at lags 2..10: k = 4 was planted; the other lags are excluded by the same
  arithmetic (every real z >= -0.80).
- B24 item 3 is not a bug. The reset keeps the plant inside the engine's model (see the E0031 notes).

## Needs a human
- Merge this PR before running gpu/E0029_bytes_gpu.py; the fixed script is only on this branch until then.
- Two items in one session goes against CLAUDE.md's "one backlog item per session". It was done because
  the prompt asked for it.
- The E0029 ledger file was not edited, because the ledger is append-only. E0031 supersedes it for the
  four pages.
- B25 check (d), E0027/E0030 on a plant corpus, was not run: it needs their 999-surrogate runs again.
- Still open: whether the audit's null rule goes into lp-experiment.
