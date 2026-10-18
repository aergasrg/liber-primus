---
id: B22
title: Running-key engine - verify short pages (cross-page key continuation, bigram scoring)
status: open
claimed_by: ""
rank: 5
ledger: [E0029]
---

# B22 Running-key engine: verify short pages

## Why
E0029's tier-1 plants are recovered 99-100/100 on pages of 141+ runes, but only 56-86/100 on the six
pages of <= 140 runes (p14 137, p22 131, p32 121, p49 66, p51 92, p55 76), so every running-key verdict
there is "not identifiable". Those six pages are 623 runes.

## Test design
1. Cross-page continuation: run `lp.runningkey` over a short page joined to its neighbour (previous
   and next page in the same section), letting the key either continue across the boundary (one DP
   pass over both pages) or restart (two independent starts, the current model). Score the joint path.
2. Bigram scoring: replace the unigram LLR by an English bigram gain in the raw29 view (the DP state
   must then carry the previous plaintext rune: 29 x source positions; cost x29, still fine on GPU).
3. Re-run tier 1 on the <= 140 bin with the same plants as E0029 (seed 28) and the same 1.65e-5
   per-page alpha; the item is done when >= 95/100 there or when it is clear neither fix gets there.
4. Re-run the E0029 sources on those six pages only.

## Notes
Do not lower the threshold to buy power; the alpha is family-wise over 55 pages x 11 sources.
