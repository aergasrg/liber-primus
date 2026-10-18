---
id: B24
title: Engine fixes from the midpoint bug hunt (F-runs in runningkey step views, plant doublet handling, E0030 hardening)
status: open
claimed_by: ""
rank: 3
ledger: [E0029, E0030]
---

# B24 Engine fixes from the midpoint bug hunt

## Why
The midpoint council bug hunt (docs/council/2026-10-18/06-gpt-6-astra-midpoint-bughunt-runningkey.md
and 07-gpt-6-astra-midpoint-bughunt-columnllr.md) found one confirmed coverage bug in `lp/runningkey.py`.
It also found several plant-generator defects shared by E0029 and E0027/E0030, and some hardening gaps
in E0030. The lead session checked each claim against the code and the real pages
(docs/council/2026-10-18/README.md, midpoint section). None of them changes a recorded verdict outside four pages.
The F-run bug does break E0029's claim of "any skip set" in the step views on those four pages.

## Confirmed (reproduced 2026-10-18)
1. **runningkey, F-runs in the step views** (`PageEvents`). Only an *isolated* ciphertext F may skip in
   step29 / unit28z1 / unit28z2. An F next to another F is always keyed, so a skip inside an FF run, or a
   skip beside a keyed F, cannot be scored.
   - Failing input: `PlantPage([0,0,1,1,1], [0,0,0], "step29", 1, -1, {0,1}, random.Random(0), Start=5)`
     gives `[5,0,0,6,7,8]`. `PageEvents` gives five keyed atoms and no skip option, so the generating
     form scores -inf on a 3-token source.
   - Real impact: 4 FF pairs on the 55 pages (pages 9, 29, 32, 36; 8 of 458 Fs), step views only. The
     raw29 view handles every F independently and is unaffected.
   - Fix: build events per F-run. Each F in a run is keyed or skipped. Literal skip: the state becomes F.
     Transparent skip: the state is kept. The keyed step out of the run is taken from the right state.
     Add a gate test with the failing input above.
   - Rerun: the E0029 step views on pages 9, 29, 32, 36 for the 7 CPU sources (minutes), with the
     same null replicates. Also apply the fix to `gpu/E0029_bytes_gpu.py` before the GPU job runs.
2. **Plant doublet multiplicity** (`MakePlant` / `PlantPage` in E0029). `DblPlain` is a set, so a
   doublet run collapses, and a doublet after the last plaintext rune is never emitted.
   - Example layouts: `[5,5,5,6,7,8]`, `[5,6,7,8,9,9]`.
   - Real impact: 0 triples, 1 terminal doublet on the 55 pages, so power numbers barely move.
   - Fix: insertion counts per gap, including gap len(Plain).
3. **Doublet resets the state after a transparent skip** (`State = Out[-1]` in the doublet branch of both
   `lp.runningkey.PlantPage` and E0027 `PlantPage`).
   - Example: runningkey `Plain=[0,1], Key=[0], unit28z2, A=1, B=-1, SkipAt={0}, Doublets={1}, Start=5`
     gives `[5,0,0,2]`; it should give `[5,0,0,7]`.
   - Fix: drop the assignment. The plant only gets harder, so the recorded power is conservative.
4. **E0027 PlantPage: a doublet overrides a requested skip** (index in both sets). Resample the conflicts,
   or report the emitted skip set instead of the requested one. `SkipSet` "random" keeps the *earliest*
   11 successes (`Chosen[:MaxSkips]`), which biases placement early; sample a uniform capped subset.

## Hardening (no verdict change found; do it with item 1)
- E0030 `NullTable`: `Var[0] = 1` gives empty columns a fictitious variance. `Var[1] = 0` exactly, and a
  float32 residual over it can blow up when every column is a singleton. The real search has a minimum
  mean column size of 3, so this does not occur in E0030. Set `Mu[0] = Var[0] = 0`, keep the scores in
  float64, and guard a zero total variance.
- E0030 `NullTable` and E0027 `SkipMasks` caches: key them by (modulus, English-model hash, draws, MaxN)
  and (NumF, MaxSkips, MaskCap). Assert that `Sizes.max() <= MaxN`.
- E0029 `Thresholds`: reject a non-positive or non-finite pooled scale.
- E0029 `MakePlant`: offset `randrange(len - PlainLength + 1)`; key start from what the source actually
  allows; the reversed-source label (`Rev != Src.Reversed`).
- `lp.runningkey.Weights`: the denominator should be Total + Modulus (effect 1e-5 per rune, cosmetic).

## Not bugs (checked; do not redo)
- E0030 mask cap (`MaxK` falls for pages with > 12 Fs): already disclosed in the E0030 ledger entry.
- E0029 byte null: `BuildSource` shuffles *before* tiling (the shuffle-after-tiling concern applies only
  to `Source.Shuffled`, which E0029 does not use for nulls).
- Polarity, reversed lattices, the rolled-count column alignment and the surrogate construction were
  all checked by the council and found consistent.

## Test design
Positive control: the failing inputs above become gate tests that fail before the fix and pass after it.
Rerun the Koan 2 / Welcome controls, and the tier-1 plants for unit28z2 with transparent skips on one
long and one 141-220 rune page. Null: E0029's existing 20 replicates for the four-page rerun. Write a
new ledger entry (follow-up to E0029) with the four-page step-view result.
