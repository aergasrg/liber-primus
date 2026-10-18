---
id: B25
title: Key-free tests of repeat-avoiding leak rules (lag-k coincidences, preceding-step gate, running-checksum gate, step-band deficit, guard and word lanes)
status: claimed
claimed_by: claude/admiring-brown-6qihly
rank: 2
ledger: [E0025, E0028]
---

# B25 Key-free tests of repeat-avoiding leak rules

## Why
The B12 target (E0028) asks for a repeat-avoiding mechanism that leaks at about 1/5 of the random doublet
rate, at independent positions, with any refractory window <= 6. The midpoint council
(docs/council/2026-10-18/08-gpt-6-astra-midpoint-ideas.md) gave 8 constructions. All share one reversible
core: each ciphertext symbol is drawn from the 28 runes other than an excluded symbol h. Usually
h = c_(i-1), which suppresses doublets. A *control law* sometimes moves h, and only then can a doublet
appear (rate 1/28 at those positions). The constructions differ only in that control law, and five of
them make sharp predictions that need **no key**, only the ciphertext and the 86 doublet positions.
Each test costs seconds. No ledger entry has tested any of them: E0028 tested the placement of the
doublet indicator (gaps, autocovariance of Z, packets), not ciphertext-context predicates or lag-k rune
coincidences beyond lag 3.

## Preregistered family (5 statistics; family-wise level 0.01; fix everything before looking)
1. **Lag-k coincidence profile** R_k = #{c_i = c_(i-k)}, k = 2..10, per section and pooled (construction 4,
   "stale exclusion register": one time in five exclude c_(i-4) instead of c_(i-1); predicts R_4 ~ 357
   where ~446 are expected, about 4.3 SD, and q = (1 - R_3) / 140). The statistic is min over k of the
   z-score (a deficit). Lag 2 and lag 3 are already reported normal; this extends to 4..10.
2. **Preceding-step gate** (construction 2: a leak is allowed only when the previous step s_(i-1) lies in a
   5-set S). Statistic: chi-square of the s_(i-1) histogram at the 86 doublets against the exposure
   histogram of all positions. Add a max-over-5-sets scan, contiguous sets {a..a+4} mod 29 only, with
   the scan inside the null. Rule predicts all 86 in S; the null predicts ~15 in any 5-set. Repeat with
   the *following* step s_(i+1) and with c_(i-2) (pre-specified: 3 conditioning variables).
3. **Running-checksum gate** (construction 3: a leak is allowed only when z = a + sum_(j<i) c_j mod 29 lies
   in a 5-residue interval, phase a per section). Statistic: per section, the max over 29 phases of the
   number of doublets whose prefix sum falls in the interval, summed over sections. Run it on three
   pre-specified running states: the sum of rune indices, the sum of prime values, and the index of
   position mod 29 (counted from the section start and from the page start). Rule: every doublet passes.
4. **Step-band deficit** (construction 7: the displaced hole lies within offsets 1..5 of c_(i-1)). Among
   non-zero steps, the frequency of {1..5} and of {24..28}, two-sided. Predicted 0.1727 vs 0.1786
   (~1.75 SD, ~25% power after correction): report it, but expect no power. A *one-hole* version
   predicts a much larger single-step deficit; the step histogram in STATE.md (step 1: 459, mean of steps 1-28 459.3)
   already argues against it. Arithmetic on the STATE.md histogram, not a test: {1..5} = 2,287 of
   12,861 (0.1778, z -0.22), {24..28} = 2,297 (0.1786, z 0.0); the five-hole prediction sits at z -1.75.
   Report the exact z with the calibrated null.
5. **Guard and word lanes** (constructions 8 and 5).
   - 8: a renewal fit of the gaps, G = R + Geom(q0); report the likelihood-ratio of R = 5 against R = 0.
     The data pass (minimum gap 6) but E0028 gave p 0.12, so expect it to stay unidentifiable.
   - 5: per word, an independent phase b in 0..4, and leaks only at positions j = b mod 5. Count same-word
     doublet pairs whose separation is not divisible by 5 (rule: 0). Compute the power from the real
     word lengths first; if the expected number of same-word pairs is < 3, report "not identifiable"
     and skip the p-value.

## Positive control (each statistic, before the real data)
Implement the common core once (lab code, PascalCase, in `lp/ciphers.py` or the experiment script):
- prefix-code solved LP plaintext into 28 digits (r <= 26 -> r; 27 -> 27,0; 28 -> 27,1);
- c_i = A[(digit + U28) mod 28] with A = 0..28 minus h, U from a seeded stream;
- swap in each control law at the parameters above.

Plant in 9 sections with the real section lengths. For each law, at the real n, check:
(a) the doublet rate lands in 0.53-0.82%;
(b) the matching statistic detects it in >= 95 of 100 plants;
(c) the memoryless law (construction 1: h moved at random on 5 of 29 selector values) is *not* flagged
    at more than the nominal rate;
(d) E0027/E0030 stay null on the plants (one corpus each is enough to confirm the council's claim that
    those tests miss this core).

## Null
- Placement statistics (2, 3, 5): 10^5 within-section permutations of the doublet positions (E0028's
  machinery, imported), with the conditioning variables recomputed at the permuted positions.
- Ciphertext statistics (1, 4): the symmetric memoryless Markov chain at the observed doublet rate
  (P(stay) = 86/12947, otherwise uniform over the other 28), 10^4 synthetic corpora with the real section
  lengths. Also run E0027's surrogate (non-zero steps permuted within pages) for statistic 1: it keeps
  the step multiset and breaks lag-k structure.
- Family-wise p from the min-p over the 5 statistics, with the same min-p in each null replicate.

## Notes
- Construction 1 (a pure Bernoulli leak) is observationally identical to the memoryless null. No placement
  statistic can test it. Dropped.
- Construction 6 (leak gated by a plaintext class five runes back) needs the plaintext. It went to B02 as a
  rule shape.
- The common core's codec, which spells IA/IO and EA as two digits, lengthens words that contain them.
  If B25 finds anything, test that prediction against word-length statistics (mean 4.47 here, 4.07 on the
  solved pages).
- Anything above its ceiling goes to the skeptic agent first.
