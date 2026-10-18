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
