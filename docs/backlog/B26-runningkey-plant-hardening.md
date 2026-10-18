---
id: B26
title: Remaining B24 items - E0029 plant doublet multiplicity, E0027 doublet/skip conflicts and skip sampling, E0030/E0029 hardening
status: open
claimed_by: ""
rank: 6
ledger: [E0027, E0029, E0030, E0031]
---

# B26 Remaining engine and plant fixes from the midpoint bug hunt

## Why
B24 fixed the F-run bug (E0031). These are the rest of its list; none of them changes a recorded verdict
(B24 checked each one). Do them together, in one session, with the gate tests B24 describes.

## Items (details and failing examples in docs/backlog/B24-engine-fixes-midpoint-bughunt.md)
1. B24 item 2: E0029 `MakePlant` / GPU `MakePlant` keep `DblPlain` as a set, so a doublet run collapses
   and a terminal doublet is never emitted. Use insertion counts per gap, including gap len(Plain).
2. B24 item 4: E0027 `PlantPage` lets a doublet override a requested skip. Its "random" `SkipSet` keeps
   the earliest 11 successes. Resample the conflicts and draw a uniform capped subset instead.
3. The B24 hardening list: E0030 `NullTable` (Mu/Var of empty columns, float64, zero-variance guard), the
   cache keys and the `Sizes.max() <= MaxN` assert; E0029 `Thresholds` scale check; the `MakePlant`
   offset, key-start and reversed-label points; the `Weights` denominator.

## Not to do
- B24 item 3 (the doublet state reset after a transparent skip). It is consistent with the engine; see
  the E0031 notes.

## Test design
Gate tests from the B24 failing inputs. Rerun only what a fix touches: E0029 power rows for item 1, E0027
tier-1 rows for item 2. Record a new ledger entry if any number moves.
