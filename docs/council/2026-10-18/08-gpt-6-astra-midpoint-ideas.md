# 08 gpt-6-astra / midpoint-ideas

- id: 20261018T223805-0d047d1d
- time: 2026-10-18T22:47:20Z
- branch: claude/nifty-ride-hy6cds
- model: gpt-6-astra, mode standard, effort xhigh, max-output 40000
- status: completed
- usage: input_tokens 1929, output_tokens 24520, reasoning_tokens 20194, total_tokens 26449

## Prompt

# Midpoint idea round: what mechanism leaks doublets at 1/5 of the random rate?

One-shot request. Runes are numbers 0..28 in Gematria Primus order (F 0, U 1, TH 2, O 3, R 4, C 5, G 6,
W 7, H 8, N 9, I 10, J 11, EO 12, P 13, X 14, S 15, T 16, B 17, E 18, M 19, L 20, NG 21, OE 22, D 23,
A 24, AE 25, Y 26, IA/IO 27, EA 28). Prime value of rune r is the (r+1)th prime (F 2 ... EA 109).

## The data

- 9 unsolved sections, 55 pages (66-277 runes each), 12,956 runes, 2,896 words, word breaks and line
  and page breaks known. IoC 0.98-1.00 in every section (random 1.00, English ~1.78).
- **The one fingerprint:** 86 doublets (c_i = c_(i-1)) in 12,947 adjacent pairs = 0.664%. Uniform
  random gives 1/29 = 3.45% (~446 expected). Ratio 0.19, i.e. about 1 in 5.2 of the "natural" repeats
  survive. Per section 3-18 doublets, consistent with one rate everywhere (chi2 6.19 on 8 df, p 0.63).
- Steps s_i = c_i - c_(i-1) mod 29: values 1..28 are uniform (chi2 normal) and independent of the
  previous rune; lag-2 and lag-3 coincidences (c_i = c_(i-2), c_i = c_(i-3)) are at the random rate.
- Doublets fall on all runes (no detectable rune preference at n = 86), inside words (0.63% of pairs)
  and across word gaps (0.80%); they are real glyphs on the page images. The suppression is present in
  plain reading order (no transposition sits on top).
- No periodicity up to 300 per section; no shared keystream between sections; one repeated 6-gram.
- Doublets are not plaintext doubled letters (chi2 255 vs English doubled-letter positions) and not a
  single rare plaintext letter mapped to step 0 (E0025).

## Doublet placement (E0028, 10^5 within-section permutations, 18 statistics)

Memoryless: family-wise p 0.09. Gap CV 0.95, Fano 0.91, no clustering, no packets (16, 29, 32, lines),
line starts 4 (null 3.9), page starts 0 (0.3), word-break doublets 23 (null 19.1). Minimum gap between
doublets 6 (null mean 2.3, p 0.12): no gaps <= 5 where ~2.6 are expected. Lab-verified exclusions:
refractory window >= 15, on/off regimes with stay >= 0.95, one per 29/32 packet, one per printed line.
Not identifiable at n = 86: rune preference, word-start preference, refractory windows <= 6.

## What the solved pages did (every key came from LP's own plain pages)

Atbash; Atbash then +3; Vigenere DIVINITY with 11 of the ciphertext F passing through without
consuming key (F-skips); Vigenere FIRFUMFERENFE (CIRCUMFERENCE with C->F) with 2 F-skips; subtract
(prime_n - 1) over the n-th rune with one F-skip. Solved plaintext has normal English doublet rates.

## What failed since the kickoff (all with planted positive controls and surrogate nulls)

- **E0027** page-local periodic keys, L 2..138, raw, step and chain-unit views, every subset of <= 11
  F-skips: family-wise p 0.26-0.77. Verified power: L 3 on pages >= 217 runes.
- **E0030** same family, column best-shift English unigram LLR, L 2..20, skip masks at every period:
  S1 3.14 vs threshold 4.17 (p 0.153). Verified: 273-rune page L 3-20, 217 runes L 3-13 (DIVINITY and
  CIRCUMFERENCE lengths), 137 runes L 3-5. 42 of 55 pages are >= 217 runes.
- **E0029** skip-tolerant page-local running keys (exact DP, any start per page, any F-skips, digraph
  lattice, raw / step / two chain-unit conventions, 4 polarities, 2 directions) from LP's own solved
  plain and cipher text, Emerson's Self-Reliance, the Mabinogion, and three small Cicada byte files:
  best page standardised 2.2-5.0 vs threshold 11.0. Verified on pages >= 141 runes (49 of 55).
- **E0028** (above): the doublet process is memoryless.
- Earlier (pre-kickoff, weaker controls): Caesar/affine/Atbash, periodic Vigenere to 600, interrupter
  databases, 294k OEIS sequences, prime/totient streams, autokey, Perl/glibc/Python PRNGs, hash pads,
  the 2014 grid and onion strings, Cicada OS files, key resets per word/line/page.

## Already filed (do not repeat): plaintext-reactive pointer rules over long sources (B02); public-domain
Cicada texts as running keys (B03); titles as cribs (B04); PRNG page-local skip-aware (B19); the grid as
ciphertext (B05); doublets as escapes for a set of rare plaintext runes (B13); self-addressing walks
through LP's plain pages (B14); deck/permutation-state keystreams, Solitaire-style (B15); expansion digits
of Cicada numbers (B16); hash pads from binary seeds (B17); timestamp seeds (B20); doublet positions as
numbers (B08); other arithmetic orders (B09); prime-Fibonacci streams (B10); self-keyed book codes (B11).

## The question

The central target: **a repeat-avoiding encryption mechanism that leaks repeats at about 1/5 of the
random doublet rate (0.66% vs 3.45%), at positions independent of each other, with any refractory
window at most 6, no rune preference detectable at n = 86, and equal leak rates inside words and
across word gaps.** It must also explain why E0027-E0030 all came back null (flat keys from LP's own
text, page-local periodic keys and the chain/step views did not show anything).

Give 8 concrete constructions. For each:
1. **Rule**: the exact encryption rule (pseudocode, a few lines), including the key source class and
   how F-skips or word breaks interact with it.
2. **Leak rate**: derive the predicted doublet rate from the rule's parameters and show that a natural
   parameter choice gives ~0.66% (e.g. a set of 5-6 of 29 symbols, a plaintext class holding ~19% of
   English, a 1-in-5 event). Say what else the parameter predicts (inside vs across word rates, per-rune
   rates, lag-2 repeats, the step histogram, the minimum gap).
3. **Why our tests missed it**: which of E0027-E0030 it defeats and how.
4. **Cheapest falsifying test** on the existing ciphertext and the 86 positions alone (no key needed if
   possible), with the statistic, its prediction under the rule and under the memoryless null, and
   whether n = 86 gives power (estimate it).
5. **Positive control**: how to plant it in solved LP plaintext through the identical pipeline.

Then rank the 8 by (prior plausibility for a 2013-2014 puzzle maker who used Vigenere with F-skips and
keys from his own text) x (cheapness of the falsifying test). Say which of the 8 the data above already
rule out and why. State assumptions; do not ask questions. Be concrete and compact.

## Reply

## Assumptions and an important constraint

I interpret “memoryless” as **not distinguishable from memoryless at 86 events**, not as a proven property. Short guards and weak context dependence remain admissible.

The observed rate has an approximate 95% interval of **0.53–0.82%**. Thus natural predictions between 0.62% and 0.71% all fit without tuning.

A trap to avoid: **“encrypt normally; replace a collision” is generally not reversible.** A length-preserving permutation of 29 plaintext symbols cannot prohibit one ciphertext symbol for every input. The constructions below therefore share an explicit, reversible 28-symbol core. Their differences are eight control laws for which ciphertext symbol is excluded.

These are constructions to falsify, not eight claims of historical plausibility. Their common codec and nonlinear key expansion are substantial prior penalties.

## Common reversible core

Encode all 29 plaintext runes into digits `0..27`:

```text
r <= 26 : emit r
r == 27 : emit 27,0
r == 28 : emit 27,1
```

This is a prefix code. It preserves word boundaries, but expands words containing runes 27 or 28. That expansion is an explicit assumption; plaintext rune lengths are not known.

For each encoded digit:

```text
h = excluded_symbol(rule, prior_state)       # one symbol in 0..28
A = sorted({0,...,28} \ {h})                 # 28 symbols
c[i] = A[(digit[i] + U28(i)) mod 28]
```

Decryption subtracts `U28(i)` from the index in `A`, then decodes the prefix code.

**Concrete key-source class:** an LP-derived phrase seeds AES-128 counter-mode streams, domain-separated by section and by purpose: digit masks, gates, and hole selection. Rejection sampling supplies unbiased `Um`. This was implementable in 2013–2014. It is scaffolding for the output constraint, **not another proposed PRNG/seed search**.

- `RN()` below means a uniformly selected rune other than `c[i−1]`.
- Every encoded digit consumes one digit mask.
- **No literal F-skips:** plaintext F is ordinary data. Word gaps consume no masks.
- State crosses words, lines, and pages, except the explicitly word-local state in construction 5.

Under the ideal-stream assumption, output is uniform over the 28 allowed symbols, regardless of plaintext frequencies. Therefore

\[
P(\text{doublet}\mid h\ne c_{i-1})=\frac1{28},
\qquad
P(\text{doublet}\mid h=c_{i-1})=0.
\]

### Why E0027–E0030 miss this common core

For all eight:

- **E0027/E0030:** there is no periodic additive key; exclusion/ranking is not addition mod 29.
- **E0029:** an LP passage used as a seed is not that passage used as a flat running key. Raw, step, and the tested chain views do not undo the changing excluded alphabet.
- **E0028:** tests event placement, not necessarily the proposed ciphertext-context predicates. It has little power against several short-memory variants below.

These are model predictions, not substitutes for planting them and running the actual tests.

---

## 1. Independent puncture failure

**Rule**

```text
g = (U29(i) < 5)
h = RN() if g else c[i-1]
```

Think of a repeat-excluding alphabet whose exclusion is displaced on five of 29 selector values.

**Leak rate and other predictions**

\[
q=\frac{5}{29\cdot28}=0.006158,
\]

or **79.7 expected doublets**. Placement is exactly iid Bernoulli under the ideal streams.

Averaging over `RN()` gives uniform nonzero steps, uniform doublet runes, equal rates across/inside words, and no minimum gap.

This is exactly the symmetric Markov model

\[
P(c_i=y\mid c_{i-1}=x)=
\begin{cases}q&y=x\\(1-q)/28&y\ne x.\end{cases}
\]

It predicts lag-2 coincidence about **3.53%**, slightly above 3.45%: only about ten excess coincidences here, insufficient to contradict “random-rate lag 2.”

**Cheapest falsification**

- Rate: compare 86 with `Binomial(12947,5/812)`; observed is only about **0.7 SD high**.
- Conditional on the event count, **no placement test can distinguish this construction from the memoryless null**. Power is exactly zero against that null.

**Positive control**

Plant using the common core. Verify the rate, uniform nonzero steps, and calibrated—not systematically significant—placement-test p-values.

---

## 2. Release after one of five preceding steps

**Rule**

Let `S={1,2,3,4,5}` and `s[i−1]=c[i−1]−c[i−2] mod 29`.

```text
g = (s[i-1] in S)
h = RN() if g else c[i-1]
```

**Leak rate and other predictions**

Nonzero steps remain marginally uniform. Hence, at stationarity,

\[
q=\frac1{28}\frac{5(1-q)}{28}
  =\frac5{789}=0.006337.
\]

Expected count: **82.0**.

Every doublet must be preceded by a step in `S`. Consecutive doublets are impossible: **minimum gap 2**, within the allowed refractory range. Rune rates and word-boundary rates are uniform. Lag-2 coincidence is

\[
(1-2q)/28\approx3.526\%,
\]

again too close to random to distinguish here.

**Cheapest falsification**

Count

\[
T=\#\{i:\text{doublet at }i,\ s_{i-1}\in S\}.
\]

- Rule: **T=86**.
- Memoryless placement null: approximately **15–16**, with SD around 3.5; use the actual exposure counts in permutations.
- Power: effectively **100%**. Even a small preregistered family of translated/reversed five-step sets is cheap to reject.

This dependence is on the **preceding step**, not on the preceding rune, so the reported independence from the previous rune does not exclude it.

**Positive control**

Plant it and require every planted doublet to pass the preceding-step predicate. The new test should be decisive while E0027/E0029/E0030 remain null.

---

## 3. Running ciphertext-checksum release

**Rule**

Initialize a secret section phase `a∈0..28`. Let

\[
z_{i-1}=a+\sum_{j<i}c_j\pmod{29}.
\]

```text
g = (z[i-1] in {0,1,2,3,4})
h = RN() if g else c[i-1]
z[i] = (z[i-1] + c[i]) mod 29
```

**Leak rate and other predictions**

The stationary joint distribution of checksum and previous rune is uniform: for a fixed checksum, the rune transition matrix is doubly stochastic. Therefore

\[
q=\frac5{29\cdot28}=0.006158.
\]

No hard refractory window; no rune preference; uniform nonzero steps. Word boundaries have no role. Hidden checksum gating creates dependence on ciphertext context without requiring a periodic or visibly clustered event process.

**Cheapest falsification**

For each section, calculate prefix sums before its doublets. Scan the 29 possible phases.

- Rule: **all doublet prefix sums occupy one translated five-residue interval**.
- Null: each such interval contains roughly 5/29 of the events.
- Power: overwhelming jointly across sections. A rough independent-exposure union bound for all 86 passing, allowing nine phases, is

\[
29^9(5/29)^{86}<10^{-52}.
\]

Use within-section permutations rather than that approximation for the reported p-value.

**Positive control**

Plant with independent section phases. The phase scan must recover a compatible phase in every section, including sections too short to identify a unique phase.

---

## 4. Occasionally use a stale exclusion register

**Rule**

Normally exclude the immediately previous rune; one time in five, exclude the rune four positions back instead.

```text
h = c[i-4] if U5(i)==0 else c[i-1]
```

This is a concrete “wrong feedback tap” mechanism, rather than an arbitrary escape flag.

**Leak rate and other predictions**

Let \(R_k=P(c_i=c_{i-k})\). Then

\[
q=\frac{1-R_3}{5\cdot28}.
\]

With the measured random-rate \(R_3\),

\[
q\approx\frac1{145}=0.006897.
\]

Crucially,

\[
R_4=\frac{4(1-R_3)}{5\cdot28}=4q\approx0.02759.
\]

Thus it predicts **suppression at lag 4**, not merely lag 1. Rune symmetry, uniform nonzero steps, and equal boundary rates survive. There is no hard refractory window.

**Cheapest falsification**

Count lag-4 coincidences.

- Rule: approximately **357**.
- Memoryless null: approximately **446**.
- Separation: about **4.3 SD**; roughly **95% power** at an eight-test Bonferroni threshold, subject to simulation calibration.

A secondary check: a doublet is impossible when `c[i−1]=c[i−4]`.

**Positive control**

Plant it and verify both identities \(q=(1-R_3)/140\) and \(R_4=4q\). Lag-4 suppression is the positive-control signal.

---

## 5. One enabled lane out of five within each word

**Rule**

Draw an independent secret phase `b∈{0,…,4}` at each word start. Let `j=0,1,…` be encoded position within that word.

```text
g = (j mod 5 == b)
h = RN() if g else c[i-1]
```

**Leak rate and other predictions**

Every position is enabled with probability 1/5:

\[
q=\frac1{5\cdot28}=0.007143,
\]

or **92.5 expected doublets**.

Boundary and interior rates are exactly equal in the ensemble. There is no section-wide period because word phases reset. Nonzero steps and doublet runes are uniform.

**Two doublets in the same word must be separated by a multiple of five.** Across a word boundary, gaps as small as one are possible.

**Cheapest falsification**

Count same-word pairs of doublets whose separation is not divisible by five.

- Rule: **zero**.
- Null: expected count approximately
  \[
  \mu_{\rm bad}=q^2
  \sum_w\#\{a<b\le L_w:(b-a)\not\equiv0\pmod5\}.
  \]
- Power: likely poor at 86 events; the expected total number of same-word doublet pairs is only order one. Calculate it from the actual word lengths.

Also count compatible same-word pairs: each has probability \(1/(5\cdot28^2)\), five times its iid-null probability.

**Positive control**

Plant with word phases. Check the forbidden-pair invariant and estimate power using the actual word-length distribution—not an assumed average word length.

---

## 6. Delayed plaintext-class release—not rare-letter escapes

**Rule**

Let `p[-5]` denote the fifth most recent fully decoded plaintext rune, carrying across word boundaries. Use the common consonant class

\[
C=\{\mathrm{R,N,S}\}=\{4,9,15\}.
\]

```text
g = (p[-5] in C)
h = RN() if g else c[i-1]
```

The sender and receiver both know this past plaintext state. During a two-digit prefix escape, update plaintext history only when that rune is complete.

**Leak rate and other predictions**

If the enabling class occupies fraction \(f\) of encoded positions,

\[
q=f/28.
\]

R/N/S total roughly **19%** in ordinary English, giving

\[
q\approx0.19/28=0.006786.
\]

Measure the actual GP/prefix-coded frequency in solved LP rather than treating 19% as exact.

This is **not B13**: a doublet can encrypt any current plaintext rune; it is a randomly thinned signal of a broad class five plaintext runes earlier.

Rune rates and nonzero steps remain uniform. There is no hard refractory window. Boundary rates are a real constraint:

\[
q_{\rm gap}=f_{\rm gap}/28,\qquad
q_{\rm inside}=f_{\rm inside}/28.
\]

The five-rune delay reduces, but does not guarantee removal of, word-ending biases.

**Cheapest falsification**

From solved LP, preregister the delayed-class frequency by word position, then test the 86 event positions with a weighted word-position likelihood.

- Null: event probability proportional only to exposure.
- Rule: proportional to the measured delayed-class exposure.
- Power: low unless the boundary fraction shifts substantially. At 86 events, an approximately **0.13–0.15 absolute shift** in the expected boundary-event fraction is needed for useful power, depending on correction.

**Positive control**

Plant the actual solved plaintext, retaining its delayed-class labels. Verify the predicted positional profile; do not select the class or delay after inspecting the unsolved events.

---

## 7. Displace the exclusion only within a five-step band

**Rule**

```text
if U5(i)==0:
    h = (c[i-1] + 1 + U5_hole(i)) mod 29
else:
    h = c[i-1]
```

Unlike construction 1, displaced holes come only from offsets `{1,2,3,4,5}`.

**Leak rate and other predictions**

Again,

\[
q=1/140=0.007143.
\]

But this predicts a small **shadow deficit** in those five nonzero steps:

\[
P(s=0)=\frac{0.2}{28},
\]
\[
P(s=x)=
\begin{cases}
0.96/28,&x\in\{1,\ldots,5\},\\
1/28,&x\in\{6,\ldots,28\}.
\end{cases}
\]

There is no rune preference, boundary effect, or refractory window. The step process is iid; lag coincidences remain near the symmetric model’s values.

**Cheapest falsification**

Among nonzero steps, count membership in `{1,…,5}`.

- Null probability: \(5/28=0.17857\).
- Rule probability: \(4.8/27.8=0.17266\).
- At this length: approximately **1.75 SD separation**.
- Power: about **54%** for a preregistered one-sided 5% test, only **23%** after an eight-test correction.

Consequently, “nonzero-step chi-square normal” does **not** already exclude this five-hole version.

**Positive control**

Plant and verify the small five-bin deficit. A useful stronger control is the one-hole version: its much larger single-step deficit should be detected.

---

## 8. Independent release, followed by a five-rune guard

**Rule**

```text
guarded = any doublet occurred in the preceding 5 positions
g = (not guarded) and (U5(i)==0)
h = RN() if g else c[i-1]
```

A leak triggers a short synchronization guard; otherwise the underlying opportunity rate is \(q_0=1/140\).

**Leak rate and other predictions**

Inter-doublet gaps are

\[
G=5+\operatorname{Geom}(1/140),
\]

where the geometric distribution starts at one. Hence

\[
q=\frac1{140+5}=\frac1{145}=0.006897.
\]

This is exactly **one fifth of \(1/29\)**.

Additional predictions:

- **Minimum gap 6.**
- Gap CV:
  \[
  \frac{\sqrt{140\cdot139}}{145}=0.962.
  \]
- Long-window Fano factor approximately **0.926**.
- Uniform rune rates and nonzero steps; equal rates across word gaps.
- Lag-2 coincidence approximately **3.522%**, not detectably different here.

The observed minimum 6, CV 0.95, and Fano 0.91 are compatible. They are not strong evidence, especially if “five” was selected after seeing the minimum.

**Cheapest falsification**

Any gap ≤5 falsifies the hard rule.

- Rule: zero.
- Null: about 2.6, using the lab’s calculation.
- Current data pass, but the lab’s calibrated **p=0.12** means this absence is not enough to establish a guard.

**Positive control**

Plant it and verify the exact renewal distribution, not just the missing short gaps. The existing gap/CV/Fano pipeline should reproduce the predicted modest underdispersion.

---

## Planting protocol for all eight

Use the same implementation, changing only the exclusion rule.

1. Prefix-encode solved LP plaintext, preserving separators.
2. Encrypt long streams with independent section domains.
3. Produce matched-size controls using the actual 55 page lengths and nine section sizes; retain inherited word boundaries.
4. Run **the unchanged E0027–E0030 pipeline**, plus the proposed new statistic.
5. Estimate power over many seeds. For word-profile tests, use the actual planted plaintext labels and boundaries.
6. Include ordinary symmetric memoryless controls at the same fitted doublet rate.

The controls should establish two different facts: the new predicate/lag test detects its planted mechanism, while the old additive-key tests generally do not.

## Ranking: plausibility × informative cheapness

All have low absolute prior because the shared codec/key expansion is not demonstrated on solved pages.

| Rank | Construction | Reason |
|---:|---|---|
| 1 | **4. Stale exclusion register** | Simple feedback mechanism; one lag count has high power. |
| 2 | **3. Ciphertext checksum** | Puzzle-friendly arithmetic; decisive phase scan without a key. |
| 3 | **2. Preceding-step release** | Extremely cheap, decisive local-context check; somewhat arbitrary allowlist. |
| 4 | **8. Five-rune guard** | Simple state machine and compatible observed summaries; currently weak discrimination. |
| 5 | **7. Five-hole band** | Alphabet-manipulation mechanism; cheap but underpowered deficit test. |
| 6 | **5. Word-local five-lane gate** | Fits preservation of word structure; too few within-word event pairs. |
| 7 | **6. Delayed plaintext class** | Requires both an arbitrary class and delay; ciphertext-only discrimination is weak. |
| 8 | **1. Independent puncture failure** | Fits perfectly, but is observationally equivalent to the fitted memoryless model. |

### What is already excluded?

**None of these eight, exactly as specified, is excluded by the supplied summaries.** Important nearby variants are:

- Construction 4 using stale taps **2 or 3** predicts substantial suppression at those lags, conflicting with the reported random rates.
- Construction 8 with refractory windows **≥15** is already excluded.
- Construction 5 with one fixed phase across whole sections would produce periodicity and is unlike the word-reset version.
- Construction 7 with one fixed displaced hole predicts a much larger step deficit; the reported omnibus result alone is insufficient to declare exclusion without the actual counts.

**Best immediate action:** run the preceding-step predicate, checksum-phase scan, and lag-4 coincidence count. Those three cost essentially nothing and can eliminate three concrete mechanisms decisively. The exact-memoryless construction cannot be eliminated by collecting more placement statistics of the same kind.
