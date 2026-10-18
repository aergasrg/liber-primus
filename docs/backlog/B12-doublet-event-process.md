---
id: B12
title: Structure of the doublet event process (spacing, clustering, autocovariance)
status: claimed
claimed_by: claude/serene-pasteur-5lrf49
rank: 12
ledger: []
---

# B12 Structure of the doublet event process

## Why
The 86 doublets are the only signal. Every mechanism proposed for them makes a different prediction
about *where* they fall relative to each other, and none of this has been tested: an independent
rare gate (hash gate, PRNG with 0 under-used, OTP with 0 excluded) gives a memoryless (geometric)
spacing; an interrupter with a refractory rule, a "one escape per packet" rule or a hidden two-state
regime gives repulsion or clustering; a plaintext-driven escape (B13) clusters inside words.
Council kickoff (docs/council/2026-10-18/02-gpt-6-astra-kickoff-cryptanalyst.md, items 3, 4, 8, 9, 10)
gave the seed-free statistics below. B08 reads the positions as numbers; this item tests their shape.
Cheap: minutes of compute.

## Test design
1. Extract the 86 doublet positions (corpus index, section, word index, position in word, line) with
   `lp.data`; keep the per-section counts.
2. Statistics on the zero-step indicator Z_i:
   - spacing distribution of gaps between consecutive doublets vs geometric with p = 86/12947
     (KS and the minimum gap; a minimum gap >= 7 keyed positions would favour a refractory rule);
   - autocovariance A_h of Z at lags 1..20 and its joint calibration;
   - within-word clustering W = sum over words of C(D_w, 2), with D_w the doublets in word w;
   - occupancy of fixed packets (16, 29, 32 positions, and printed lines): count of packets holding
     two or more doublets;
   - per-section counts vs binomial with the section lengths.
3. Null: 10^5 permutations of the doublet positions within each section (per-section counts fixed),
   giving the ceiling for every statistic; report two-sided p with the five statistics counted.
4. Positive control: plant each alternative (refractory gap 7, Markov regime with stay 0.95/0.80,
   one-per-32-packet) at the same rate 86/12947 in 10 synthetic corpora and confirm the statistic
   that should see it does, at the same trial count.
5. Verdict per alternative: consistent with memoryless, or which structure is seen.

## Notes
If everything is memoryless, the doublets carry no placement information and B08 is downgraded.
If clustering inside words appears, B13 goes first.
