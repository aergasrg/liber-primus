# 04 gpt-6-astra / kickoff-negatives

- id: 20261018T173711-118c6898
- time: 2026-10-18T17:43:54Z
- branch: claude/stoic-feynman-g6muzj
- model: gpt-6-astra, mode standard, effort high, max-output 25000
- status: completed
- usage: input_tokens 4508, output_tokens 19673, reasoning_tokens 12948, total_tokens 24181

## Prompt

You are auditing a cryptanalysis lab's negative results. Below are our three most important
negative tests, with exactly what each covered, how it scored, what positive control and null it
used, followed by the full evidence file for the cipher text. Question: how could each of these
three tests have missed a real signal? For every concrete gap you find give: (a) the mechanism by
which a true key of that family would score below our noise ceiling (be quantitative where you can:
for example how many aligned runes survive before the score falls under the ceiling); (b) whether the
positive control would also have failed to expose the gap (that is, the plant did not contain the
feature); (c) the exact rerun that closes the gap: coverage change, the feature to plant in the
control, the null to use, and the statistic and threshold that would then count as a hit; (d) a
rough cost (number of candidate keys x window length). Order gaps by how likely they are to hide a
real key given the fingerprint. Also say, for each test, which gaps are NOT worth rerunning and why.
Answer as three numbered sections (T1, T2, T3) plus a short ranked summary, no preamble, no
questions back.

## T1 = ledger E0002: periodic Vigenere / Beaufort (external result, community tool LPA)

- Hypothesis: a repeating key of period <= 300 per section or <= 600 over the whole corpus,
  Vigenere (c - k) or Beaufort (k - c), key symbols mod 29.
- Coverage: periods 1-300 for each of the 9 sections separately and 1-600 over the concatenated
  corpus; variants with and without F-skips (a ciphertext F that consumes no key) and with
  skip-on-collision (skip when plaintext would equal the key symbol). Detector: IoC by period
  (column IoC) and column statistics.
- Control: none recorded. Null: none recorded. Result: no period stands out.
- Related: no shared keystream between any two sections at overlaps of 600 or more (depth test).
- Known weaknesses we already see: the sections contain several pages each and the solved keys
  change per page; the F-skip ordinals were presumably fixed rather than searched; we do not know
  whether periodicity was tested on the step sequence s_i = c_i - c_(i-1) (the chain form) as well
  as on the raw runes.

## T2 = ledger E0008: running keys from known texts (external result, LPA)

- Hypothesis: the key is a known text: Liber Primus's own solved plaintext pages, Liber Primus's
  own ciphertext (other pages), Emerson's Self-Reliance, The Mabinogion.
- Coverage: every offset of each text against every section, rigid alignment (one key symbol per
  ciphertext rune, no skips), English score of the output.
- Control: none recorded. Null: none recorded. Result: nothing above noise.
- Known weaknesses: every keyed solved page has F-skips, so one skip early in a window breaks the
  alignment; direction (reversed key), sign (Beaufort), the chain form (key applied to steps mod
  28), the mapping of English text into 29 runes (TH, NG, EA, OE, AE, IA/IO, EO are single runes,
  so a text has several rune spellings), and whether the key restarts per page were probably not
  all covered. Our planned rerun is backlog B01, a skip-tolerant engine.

## T3 = ledger E0019 (and E0020): PRNG keystreams, lab run with control and null

- Hypothesis: the key is int(rand()*29) or int(rand()*28) from Perl's drand48 (seed = srand
  argument), or rand() % 29 / % 28 from glibc, or Python's Mersenne Twister randrange(29/28)
  (Python 3) or int(random()*29/28) (Python 2), for some seed.
- Coverage: seeds 0..1,048,575 (Perl, glibc) plus 22 Cicada numbers, seeds 0..262,143 (Python);
  only the first 300 runes of each section, aligned at the section start, with no burn-in; four
  forms: raw c - k and c + k mod 29, and chain form u - k and u + k mod 28 where u_i = s_i - 1 over
  the non-zero steps.
- Detector: normalised IoC of the 300 output symbols (random 1.00 +- 0.03, English about 1.78
  raw / 1.81 chain). The sweep kept the best seed per section and form.
- Control: drand48 seed 777777 planted over solved plaintext (no skips), swept over seeds
  777000-777999, recovered at IoC 1.875 raw / 1.810 chain. The generators were validated bit-exact
  against perl and libc.
- Null: extreme value of IoC over about 10^6 random trials on 300-rune windows: ceiling 1.20-1.25.
- Result: best 1.23 on 300 runes; the same seeds fall to about 1.01 on the whole section. Negative.
- Known weaknesses: no skips in the plant or the scan; the key is assumed to start at the first
  rune of each section; no offsets, no discarded leading outputs; 20-bit seed space only; the
  per-page key change seen in the solved pages was not modelled.

## Shared evidence file follows

# Liber Primus kickoff brief (shared body for the kickoff calls)

Conventions: runes are written as numbers 0-28 in Gematria Primus order, or as their Latin values.
Arithmetic is mod 29 unless stated. "Section" means one of the 9 unsolved sections below.

## 1. Gematria Primus (index: latin, prime)

0:F,2 1:U,3 2:TH,5 3:O,7 4:R,11 5:C/K,13 6:G,17 7:W,19 8:H,23 9:N,29 10:I,31 11:J,37 12:EO,41
13:P,43 14:X,47 15:S/Z,53 16:T,59 17:B,61 18:E,67 19:M,71 20:L,73 21:NG,79 22:OE,83 23:D,89
24:A,97 25:AE,101 26:Y,103 27:IA/IO,107 28:EA,109

## 2. How every solved page was solved (2014 Liber Primus, 2014-2016 community work)

| Page | Method |
| --- | --- |
| A Warning | Atbash (index -> 28 - index) |
| Welcome | Vigenere, key DIVINITY; 11 ciphertext F's (rune 0) pass through without consuming key: the 4th,5th,6th,7th,10th,11th,14th,18th,20th,21st,25th F |
| Some Wisdom | plain; ends in a word/number square |
| Koan 1 | Atbash then +3 |
| The Loss of Divinity | plain, contains a numbered list |
| Koan 2 | Vigenere, key FIRFUMFERENFE (CIRCUMFERENCE with C->F), 2 F-skips |
| An Instruction | plain; a 5x5 number square whose rows sum to 3301 |
| An End | c_i = p_i - (prime_n - 1) where prime_n walks the primes; one F-skip (the 4th F) |
| Parable | plain |

Facts: every key came from the book's own plain pages (DIVINITY, CIRCUMFERENCE, the primes).
Every keyed solved page has "F-skips": a ciphertext F that is a literal plaintext F and does not
consume a key symbol. Skips are rare (1-11 per page) and irregular. Keys change per page.

## 3. The unsolved material: 9 sections, 12,956 runes, 2,896 words

| Section | Runes | Doublets |
| --- | --- | --- |
| p0-2 | 729 | 4 |
| p3-7 | 1,145 | 6 |
| p8-14 | 1,729 | 9 |
| p15-22 | 1,903 | 10 |
| p23-26 | 1,021 | 11 |
| p27-32 | 1,433 | 13 |
| p33-39 | 1,680 | 12 |
| p40-53 | 3,008 | 18 |
| p54-55 | 308 | 3 |

Word boundaries (spaces/dots) and line and page breaks are in the clear. Mean word length 4.47 runes
(solved plain pages 4.03-4.07); two-rune words 15.5%.

## 4. The fingerprint

- Index of coincidence (IoC, normalised so uniform random = 1.00) is 0.98-1.00 in every section.
  English in runes is about 1.78. Unigram, bigram, lag-2 and lag-3 statistics are all flat.
- **The one anomaly:** 86 doublets (c_i == c_(i-1)) in 12,947 adjacent pairs = 0.66%. Uniform
  random text gives 3.45%, about 446 expected. Every section shows the deficit (see table).
- Step histogram, s_i = c_i - c_(i-1) mod 29, for steps 0..28:
  86, 459, 504, 440, 438, 446, 430, 470, 426, 510, 497, 454, 449, 503, 474, 469, 448, 404, 433,
  474, 467, 462, 421, 486, 467, 467, 457, 475, 431. Steps 1..28 are uniform (chi-square normal)
  and independent of the previous rune. Lag-2 and lag-3 coincidence rates are normal (about 3.4%).
- Doublets fall on all runes, inside words (0.63%) and across word gaps (0.80%); they are real
  distinct glyphs on the page images, not transcription artefacts.
- Doublet suppression appears in plain reading order, so no transposition sits on top of whatever
  produces it.
- No periodicity up to 300 per section or 600 over the corpus (IoC by period, kappa tests).
  No shared keystream between any two sections at overlaps of 600+ (no depth).
- One repeated 6-gram (D J U B E I = 23 11 1 17 18 10) at corpus positions 6555 and 12950
  (0-based, sections concatenated in order). Nothing else repeats beyond chance.
- Doublets are not plaintext doubled letters: English in runes doubles at 3.49%, and the
  in-word position profile of the 86 doublets does not match doubled letters or any single rune.

## 5. Working model

The only model found so far that fits all of section 4: a **chain (differential) cipher**
c_i = c_(i-1) + s_i, with s_i drawn from 1..28 by a flat, aperiodic key, so a step of 0 is rare
(the 86 doublets). Equivalently the ciphertext is a running sum of a flat key, and what we see
is the 0-step deficit. Open question: what source gives s_i, and why does step 0 occur 86 times
at all (leakage? plaintext doublings? an interrupter rule?). An alternative we cannot exclude:
the key is a true one-time pad with 0 deliberately excluded or under-used, in which case nothing
is recoverable without the pad.

## 6. Leads with exact values (unused or only partly used)

- 8x32 grid on p40-53: two-character tokens over digits 0-9A-Za-x, value = 60*first + second,
  giving 256 bytes spanning 0..255, entropy 7.17 bits/byte. First bytes hex cbe7a7ba61ed7eb7.
  Not an RSA modulus (big-endian it is divisible by 2, 5, 43 and 53).
- Page-56 128-hex-digit hash (algorithm unconfirmed, SHA-512 or BLAKE2b assumed):
  36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fda
  f1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4
- Page-15 4x4 square: 3258 3222 3152 3038 / 3278 3299 3298 2838 / 3288 3294 3296 2472 /
  4516 1206 708 1820. Each cell = 3301 +- a prime whose prime index is a Fibonacci number
  (a Zeckendorf spiral).
- Numbers printed inside the unsolved pages: a numbered list 1-5 in p33-39; a lone numeral 7 in
  p8-14; cuneiform numerals 1033 and 3301 in the p33-39 artwork.
- 2012 P.S. 131-digit semiprime = 99554414790940424414351515490472769096534141749790794321708050837
  x 104593961812606247801193807142122161186583731774511103180935025763 (both prime).
- 2013 cookies: 167 = 6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6,
  761 = 7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5.
- Telnet prime list (2013) missing the primes 73..1223. Prime-length runs of spaces in the 2012,
  2014 and 2015 signed messages. "9133" at the end of the 2014 onion-4 string.
- Numbers already tried as keys: 3301, 1033, 761, 167, 1231507051321, 845145127, 1595277641,
  PGP key ids 7A35090F / 181F01E57A35090F.
- Cicada's 2016 signed hint: Liber Primus is the way; its words are the map, their meaning is the
  road, and their numbers are the direction.

## 7. What has been excluded (ledger families, one line each; "control" = planted-key recovery)

1. E0001 classical substitution / transposition: excluded by theory, IoC would stay 1.78.
2. E0002 periodic Vigenere/Beaufort: periods 1-300 per section, 1-600 corpus, with and without F-skips. External, no lab control.
3. E0003 short keys (<=32) with every rune as interrupter, first 20 interrupts: best IoC 1.3-1.4, overfit to free choices. External.
4. E0004 all 294k OEIS sequences mod 29, first 40 terms, small offsets, all shifts, F-skip combos. External, no control.
5. E0005/E0006/E0017 selected sequences (primes, totient, naturals, squares, triangular, Fibonacci, pi digits, prime gaps), raw and chain form, 14 step orderings, forwards and backwards from section ends, prime-value feedback rules. Lab control IoC 1.93, null 1.00, best 1.13.
6. E0007 ciphertext autokey lags 1-60 and plaintext autokey lags 1-3 with all primers, raw and chain. External.
7. E0008/E0012/E0024 running keys with rigid alignment: LP's own solved text and ciphertext, Self-Reliance, The Mabinogion, the 2014 growing string, raw page-image bytes, 2013 Cicada OS files (761.MP3 etc), every offset, both signs. Rigid alignment means one F-skip breaks the match; a skip-tolerant rerun is backlog B01.
8. E0009 per-word shifts and Playfair-style pair ciphers. External.
9. E0010 crib dragging (community, undocumented): inconclusive; systematic title cribs are backlog B04.
10. E0011 OutGuess on all 75 page images, no key and 96 keys: only the known 2014 payloads. A 2025 claim of data on every page is LSB noise.
11. E0013 page-56 hash preimage: 692k archive files and onion lists with SHA-512 and BLAKE2b, no match.
12. E0015 key resets per word, sentence, line, page (same in-unit position shares a key symbol), raw and chain: control z 5.6-6.1, null z about 3, real z -0.7..+1.0.
13. E0016 pages in depth (pairs sharing a keystream from their first rune): 7 pairs above z 3 = null median. No plant.
14. E0018 shift arithmetic after re-indexing runes in Latin-alphabetical order: 24 keywords and 9 sequences, control 1.76, best 1.08.
15. E0019/E0020 PRNG keystreams: Perl drand48 and glibc rand() seeds 0..1,048,575 plus 22 Cicada numbers; Python Mersenne Twister seeds 0..262,143; first 300 runes of each section, raw and chain, both signs. Control 1.88 raw / 1.81 chain, extreme-value null 1.20-1.25, best 1.23.
16. E0021 hash-derived pads: 96 Cicada words x 7 hashes x 3 chaining modes x 2 reductions = 4,032 pads, first 300 runes, 4 forms. Control 1.88, null about 1.2, best 1.16.
17. E0022 unused Cicada numbers written in base 29 as running keys (P.S. number and factors, cookies, hash, parable number, PGP ids), both digit orders, both signs, each section start: all below the random 99th percentile.
18. E0023/E0026 the 256-byte grid as running key (every offset, raw and chain, bytes and reversed) and as a global book code into LP's words: null 1.17-1.27, best 1.18; book code below the random 99th percentile.
19. E0025 doublets as plaintext doubled letters or one rare letter: chi-square 255 against 18.5 critical.

Scoring tools available: IoC (raw mod 29 and chain mod 28), unigram LLR per rune (English +0.40,
random -0.6 to -0.84), bigram gain per rune (English +0.5), FFT running-key scans, planted-key
controls (lp.controls), permutation and extreme-value nulls. Open backlog: skip-tolerant running
keys (B01), plaintext-reactive keys (B02), public-domain Cicada texts (B03), title cribs (B04),
grid as ciphertext (B05), other stego tools (B06), non-English scoring (B07), doublet positions as
numbers (B08), other arithmetic orders (B09), prime-Fibonacci streams (B10), self-keyed book codes
indexed by page/line/sentence (B11).

## Reply

## 1. T1 — Periodic Vigenère / Beaufort

**Interpretation and calibration.** “Missed” below includes an omitted nearby family, not necessarily a failure of the stated raw-rune test. T1 and T2 have neither a recorded control nor a recorded null, so their actual detection ceilings and power are unknown. T3’s **1.20–1.25 ceiling cannot be transferred to them**, or to a larger adaptive search.

For the reruns below, use this common hit rule:

- Freeze the search space and scoring procedure before examining results.
- Generate **999 null corpora** by permuting nonzero steps within pages, retaining zero-step positions, page/word boundaries and lengths, then reintegrating from random section-initial runes. This preserves the principal fingerprint. Recompute F positions rather than retaining the observed F positions independently of the surrogate ciphertext.
- Run the **entire search**, including alignment optimization and candidate selection, on each null. A hit has max-search empirical \(p=(1+\#\{\text{null maxima}\geq S\})/1000\leq0.01\). This is a 1% family-wise threshold per test; divide the allowance by three if requiring 1% across this entire audit.
- Require feature-bearing plants to survive that same procedure. A concrete acceptance target is recovery in **at least 95 of 100 plants** covering different plaintext windows and keys.
- The costs below are search costs. Full max-null calibration costs approximately **1,000 times as much**. A cheaper valid alternative is discovery on a training block followed by a separately calibrated, untouched continuation, with the key, source offset, period and generator already frozen. Do not validate a page-local hypothesis by demanding that it decrypt subsequent independently keyed pages.

The 28-symbol chain encoding is an assumption: **freeze and document the encoding used by the existing chain control**. Modulo 28 arithmetic alone does not specify how 29 plaintext runes and exceptional zero steps are represented.

### Gap 1: The periodic signal may exist in steps, not ciphertext runes — highest fingerprint relevance

**(a) Mechanism.** If
\[
u_i=(p_i+k_{i\bmod P})\bmod28,\qquad s_i=u_i+1,\qquad c_i=c_{i-1}+s_i\bmod29,
\]
then column statistics of \(c_i\) need not expose period \(P\). The running sum mixes the plaintext and key history. A perfectly periodic key in the step domain can therefore coexist with nearly uniform raw-rune columns.

This is not ordinary raw Vigenère escaping a complete test; it is an **untested differential extension**. It directly accommodates the nonzero-step fingerprint, unlike an ordinary uniform mod-29 pad.

**(b) Control.** There was no recorded control. A raw Vigenère plant would not expose this gap.

**(c) Exact rerun.**

- Test three views: raw \(c_i\) mod 29; steps \(s_i\) mod 29; and \(u_i=s_i-1\) mod 28 on nonzero steps.
- Test each page independently, periods \(1\ldots300\), retaining the section-level scan as a comparison.
- Omit the incoming edge to each page from scoring unless its initialization rule is explicitly modeled.
- For mod-28 chains, test both “zero step consumes a key symbol” and “zero step does not consume a key symbol”; mixed handling is addressed in Gap 3.
- Plant periodic **integrated** chains, including the declared zero-step convention, rather than merely encrypting plaintext with raw Vigenère.
- Use pair-weighted column IoC, standardized against the same window/period null. Threshold the maximum standardized statistic by the common max-null rule. Recover column shifts and check linguistic output before calling the result a recovered key.

**(d) Cost.** With \(N=12,956\), three views and 300 periods:
\[
3\times300\times N\approx1.17\times10^7
\]
symbol visits, before skip searches. These are **period hypotheses**, not enumeration of all \(29^P\) possible keys.

### Gap 2: Page-local keys can erase section-level periodicity; long page-local periods can be statistically unidentifiable

**(a) Mechanism.** A section column can mix plaintext encrypted under several unrelated page keys. If subgroup \(a\) contributes fraction \(w_a\), and cross-subgroup coincidences are approximately random, the normalized column-IoC excess is approximately
\[
I_{\rm col}-1\approx(1.78-1)\sum_a w_a^2.
\]
Four equally weighted independent page keys give approximately **1.195**; six give **1.130**. These are illustrations of dilution, not claims about T1’s undocumented ceiling.

There is a second problem: after moving to pages, long periods have too few repeated column observations. For a 230-rune page:

- Period 100 supplies only **160 within-column pairs**.
- Under a uniform mod-29 null, normalized column IoC has approximate standard deviation
  \[
  \sqrt{28/160}=0.42.
  \]
  An English excess of 0.78 is less than two standard deviations before searching hundreds of periods.
- Period 200 supplies only **30 pairs**.
- Period \(P\geq230\) supplies **none**.

Thus a real long page-local key may leave no detectable periodic signature in one page.

**(b) Control.** No recorded control. A single key repeated throughout a section would not expose page mixing or short-page power loss.

**(c) Exact rerun.**

- Segment at the actual 56 page boundaries; do not concatenate independently keyed pages for column statistics.
- Plant independent keys on successive pages, with periods spanning short, intermediate and near-page-length regimes.
- Report power **by page length and period**, not one overall recovery percentage.
- Use the same column statistic and max-null threshold as Gap 1.
- Where plants demonstrate inadequate power, report **“not identifiable at this length”**, not “excluded.” Closing that remaining gap requires an additional constraint: a keyword dictionary, a repeated key on another page, or other independently justified key structure.

The 600-rune depth result does not close this gap: individual pages average only about 231 runes, and page-specific keys need not be reused.

**(d) Cost.** Page segmentation itself remains at most
\[
300\sum_j L_j\approx3.89\times10^6
\]
symbol visits per representation. Exhaustively recovering an unconstrained period-\(P\) key is a different problem, with \(q^P\) possibilities.

### Gap 3: Fixed F-skip ordinals and unspecified zero-step consumption can destroy the column grouping

**(a) Mechanism.** One missed non-consuming F shifts every later key-column assignment by one until another event compensates. Several skips partition a page into runs with different effective phases. If \(r\) equally sized phase groups have effectively unrelated key shifts,
\[
I_{\rm col}\approx1+\frac{0.78}{r}.
\]
Four groups already give about **1.195**; twelve give **1.065**.

“Skip all F,” “skip these fixed F ordinals,” and “skip on a specified collision” are not equivalent to the irregular selected-F behavior in the solved pages.

For a mod-28 chain, silently dropping all 86 zero steps also assumes that none consumed a key symbol. If that assumption is wrong, each such event creates another phase error. Their mean spacing is approximately 151 edges—large enough that a single error can spoil half a 300-symbol window.

**(b) Control.** No recorded control. A no-skip plant, an all-F-skip plant, or a plant using exactly the scanner’s fixed ordinals would all fail to expose the general irregular-skip gap.

**(c) Exact rerun.**

- Enumerate every subset of ciphertext F positions with **0–11 non-consuming F events per page**. This is a declared, evidence-based bound, not coverage of unlimited skips.
- In chain mode, distinguish two explicit F conventions:
  1. literal F becomes the new chain state;
  2. inserted F is transparent to the chain state, so differences are recomputed between retained runes.
- For each zero step in mod-28 mode, allow either key advance or hold, without scoring that exceptional edge as an ordinary 28-symbol plaintext symbol.
- Plant irregular F masks—including the known Welcome-style pattern—and plants with both zero-consumption conventions. Include cases where the first event occurs early.
- Apply the same maximum-column-statistic null, with all mask and convention choices included in the maximization.

**(d) Cost.** Let \(F_j\) be the number of ciphertext F’s and \(Z_j\) the number of zero edges on page \(j\), and define
\[
A_j=\sum_{h=0}^{\min(11,F_j)}{F_j\choose h}.
\]
An exact mask search costs approximately
\[
300\sum_j L_j A_j
\]
per raw representation, and up to
\[
300\sum_j L_j A_j\,2^{Z_j}
\]
per chain-state convention.

For a page with eight F’s, \(A_j=256\). Actual costs depend strongly on the largest per-page F counts. **Do not claim a simple 12-state dynamic program exactly maximizes column IoC:** that objective depends on accumulated column histograms.

**Not worth rerunning for T1**

- **Beaufort versus Vigenère solely as an IoC detector change.** Column reflection preserves IoC. It matters when decoding and scoring language, not for the existence of column coincidence.
- **Different initial key phases solely for column IoC.** They relabel columns.
- **Unconstrained very long page-local periods.** Beyond the available repetitions, this is an identifiability limit, not a coverage defect repairable by more CPU.
- **Arbitrary interrupter runes and unrestricted free skips.** E0003 already shows their overfitting potential. Start with the solved-page F mechanism and the chain-specific zero events.
- **Another same-key, same-position reset scan without new features.** E0015 already weakens that narrow model. Independent page keys remain a different hypothesis.

## 2. T2 — Running keys from known texts

T2’s strongest unresolved issue is **alignment**, followed by the chain representation and rune tokenization. There was no positive control, so “the plant lacked this feature” is not literally applicable: **there was no plant to challenge any of these assumptions**.

Use a frozen rune-language model. For exact skip-alignment search, an additive unigram LLR permits tractable dynamic programming; adding an exact bigram objective requires plaintext-context states. Calibrate the complete optimized score against the common null. Keep external source texts fixed; when LP ciphertext pages serve as sources, regenerate their surrogate versions jointly with the target corpus.

### Gap 1: Irregular F-skips and independent page starts break rigid running-key alignment

**(a) Mechanism.** With an aperiodic running key, one missed skip generally makes the rest of the window wrong—not merely assigned to another useful periodic column.

For \(m\) correctly aligned runes in a window of \(n\), let \(f=m/n\). Using the supplied unigram-score expectations, a rough mixture gives
\[
E[\mathrm{LLR/rune}]\approx0.40f-b(1-f),\qquad b=0.60\ldots0.84.
\]
To exceed a per-rune threshold \(\tau\), approximately
\[
f>\frac{\tau+b}{0.40+b}.
\]
Even to exceed **zero**, about **60–68%** of the window must remain aligned: roughly **181–204 of 300 runes**. A skip after 100 good runes leaves an expected score around **−0.27 to −0.43 per rune**.

These are approximations: wrong-alignment running-text outputs can retain correlations, so the actual null must be measured.

A page-local source restart or source change causes the same dilution when the whole section is scored. Scanning every source offset at a section start does not test independent source offsets at later page starts.

**(b) Control.** None recorded. A rigid, section-long plant would also miss both features.

**(c) Exact rerun — the essential B01 specification.**

- Search every source offset against **every page**, allowing independent source selection and offset per page.
- Allow 0–11 literal, non-consuming F events per page.
- Do not require the same recovered offset to continue across the next page.
- Plant irregular masks with first skips before rune 50, around rune 100, and late in the page; plant adjacent pages using different source offsets.
- Optimize the frozen additive language score over allowed alignments. Use the max-null \(p\leq0.01\) threshold; include all source offsets, pages and skip paths in the null search.
- Check recovered text with a separate bigram/word-boundary score or a frozen-key continuation.

**(d) Cost.** Let \(K\) be the total number of source starting positions searched. With at most 11 F-skips, a known-key unigram DP costs roughly
\[
K\times12\sum_j L_j \approx155{,}472K
\]
state-symbol evaluations per representation/direction/arithmetic form. Exact bigram optimization can add up to 29 plaintext-context states.

This is a substantial multiplier over a rigid FFT scan; a rigid shortlist followed by skip correction **does not close the gap**, because the true offset may never enter the shortlist.

### Gap 2: The known text may key the nonzero steps rather than the raw runes

**(a) Mechanism.** Subtracting a running text from \(c_i\) does not invert a cipher that adds that text to \(u_i=s_i-1\). Essentially no correctly decoded plaintext need survive, even with the correct source and offset.

Zero-step handling then becomes an alignment issue of its own. Dropping a zero that consumed a key symbol has the same downstream effect as missing an F-skip.

**(b) Control.** None recorded. A raw running-key plant would not expose this gap.

**(c) Exact rerun.**

- Run B01 on raw mod-29 symbols, mod-29 steps, and mod-28 nonzero steps.
- Use the same declared 28-symbol codec as T1/T3.
- In mod-28 mode, allow advance/hold at each zero edge; do not arbitrarily assign every zero a fixed plaintext rune. E0025 argues against that simple interpretation.
- Include both explicit F/chain-state conventions from T1.
- Plant integrated running-key ciphertext with early F events and zero events, including mixed key consumption.
- Use the optimized language-score max-null threshold, not the old rigid-output noise level.

**(d) Cost.** Three representations multiply the basic source-offset scan by roughly three. If \(D_j=11+Z_j\) bounds non-consuming events, the alignment component is approximately
\[
K\sum_j L_j(D_j+1)
\]
per fixed representation/convention. The additional F-state convention is another explicit factor.

### Gap 3: A single canonical English-to-rune spelling can exclude the correct running text

**(a) Mechanism.** A source spelled with TH as one rune differs in length from one spelled T,H. The same applies to NG, EA, OE, AE, IA/IO and EO. One such discrepancy can destroy alignment for the remaining window.

For example, a first mismatch after 100 aligned symbols produces the same roughly negative LLR mixture calculated above. “Every offset” does not repair a length discrepancy **inside** the window.

A global “always collapse digraphs” versus “never collapse digraphs” comparison is also incomplete: the real spelling could vary occurrence by occurrence.

**(b) Control.** None recorded. A plant made using the scanner’s own canonical tokenizer would necessarily hide this gap.

**(c) Exact rerun.**

- Freeze all other transliteration conventions to the lab’s documented LP transcription rules.
- Build a tokenization lattice permitting each listed digraph either as its single GP rune or as its component runes, subject to nonoverlapping segmentation.
- Search all source starting positions through that lattice, jointly with the bounded skip alignment.
- Reverse **rune-token sequences**, not Latin characters, when testing reversed keys.
- Plant mixed tokenizations within the same source passage, with an early ambiguity and later ambiguities in both directions.
- Keep the lattice and its scoring/prior identical in real and null searches. This flexibility can otherwise manufacture English-looking output from noise.
- Use the complete max-null language-score threshold.

**(d) Cost.** With a maximum token length of two Latin letters, a conservative exact bound is
\[
O\!\left(K\sum_j(D_j+1)L_j^2\right)
\]
per arithmetic form, before bigram-context states. This is roughly an additional window-length factor over a fixed-tokenization DP. The source lengths and actual ambiguity counts are not supplied, so a credible numerical total cannot be given.

### Gap 4: Reversal and plaintext polarity may be absent from the recorded coverage

**(a) Mechanism.** The correct source read backward is not found by forward offset scanning. Likewise, a Beaufort plaintext \(p=k-c\) is the reflection of \(c-k\): **identical IoC, but generally a bad English score** if scored without reflection.

The related ledger says later running-key tests tried “both signs.” That must be reconciled with executable coverage: \(c-k\) and \(c+k\) are not, by themselves, all plaintext polarities.

**(b) Control.** None recorded. A forward Vigenère plant would not expose either omission.

**(c) Exact rerun.**

- At each source offset, test forward and reversed rune sequences.
- Test \(p=ac+bk\bmod q\), \(a,b\in\{-1,+1\}\), in the declared raw or step domain.
- Plant a reversed source with Beaufort polarity and a mixed-tokenization source.
- Use the same full-search language-score null and threshold.
- If preserved E0012/E0024 logs demonstrate that a particular form was already covered, mark it covered rather than rerunning it as a supposed discovery.

**(d) Cost.** At most **eight direction/polarity forms per representation**. This is cheap relative to unrestricted tokenization and skip alignment.

**Not worth rerunning for T2**

- **More rigid scans of the same texts against whole sections.** They reproduce the best-supported failure mechanism.
- **An enormous new public-domain corpus before B01 works on feature-bearing plants.** Expanding source coverage cannot repair alignment or tokenization.
- **Unbounded edits or arbitrary key-word selection.** These turn known-text testing into a highly flexible model with a severe selection penalty.
- **A broad non-English search as the first repair.** The solved material favors English. Retain IoC as a cheap language-independent diagnostic, but fix alignment and representation first.
- **Duplicate sign tests already demonstrated by logs.** Spend effort resolving provenance, not re-labeling existing coverage.

## 3. T3 — PRNG keystreams

The plant establishes that a **no-skip drand48 key at the tested origin** can be recovered. The bit-exact checks substantially support the Perl/glibc implementations. Neither fact validates the omitted alignment, seed and page models.

A useful quantitative approximation is
\[
E[I]\approx1+(I_E-1)\frac{m(m-1)}{n(n-1)},
\]
where \(m\) symbols are correctly decoded and the rest are approximately uniform and independent.

For \(n=300\):

| Ceiling | Minimum aligned runes, raw \(I_E=1.78\) | Minimum aligned runes, chain \(I_E=1.81\) |
|---|---:|---:|
| 1.20 | 153 | 150 |
| 1.25 | 171 | 167 |

These numbers apply to the old fixed-window ceiling, **not** the expanded searches proposed below.

### Gap 1: F-skips and zero-step consumption can hide an otherwise covered seed

**(a) Mechanism.** One early missed skip changes the PRNG index for essentially every subsequent symbol. If only the first 100 symbols survive, expected raw IoC is approximately **1.086**, comfortably below the ceiling. With only 150 surviving, it is approximately **1.194**.

The chain scan already omits zero steps from its output alphabet, but it must separately specify whether a zero consumed a PRNG output. Incorrectly dropping a consuming zero causes the same phase loss.

**(b) Control.** **Yes, the plant failed to expose this gap:** it contained no skips. The reported chain recovery also does not establish coverage of exceptional zero events unless those events were explicitly planted.

**(c) Exact rerun.**

- Apply the bounded page-local F/zero alignment engine from T2 to every originally searched generator/seed pair.
- Include both declared F/chain-state conventions.
- Plant 1, 2 and 11 irregular F-skips per page, including an early event; separately plant advancing and non-advancing zero events.
- Add plants for glibc and both Python output recipes, rather than relying solely on drand48.
- For tractable exact alignment search, optimize additive language LLR and calibrate its full-search maximum. Report IoC on recovered candidates as a secondary statistic.
- If retaining IoC as the optimized objective, enumerate alignment masks or retain the required count state: **a small key-index DP does not exactly optimize IoC**.
- A hit is max-null \(p\leq0.01\), followed by a continuation under the same page-local key and declared alignment rules.

**(d) Cost.** Counting Python 2-style and Python 3-style output recipes separately gives approximately
\[
G=2(1{,}048{,}576)+2(262{,}144)=2{,}621{,}440
\]
generator/recipe/seed entries.

With four original forms and a 12-state skip bound:
\[
G\times4\times12\times12{,}956\approx1.63\times10^{12}
\]
state-symbol evaluations for full-page coverage, before extra zero states and conventions. Restricting scoring to page-local 300-rune windows lowers this total.

### Gap 2: Page changes, later origins and burn-in can make the whole-section “confirmation” actively misleading

**(a) Mechanism.**

- Correct seed, wrong burn-in: the tested output is essentially wrong from the first symbol.
- Correct key beginning later in a section: the first 300 runes may contain none of its plaintext.
- Correct first-page key followed by a page change: only the first page contributes signal.

In particular, **163 correct symbols out of 300** give expected raw IoC approximately **1.23**. If the section has 1,433 runes and the remaining runes use other keys, the same candidate falls to approximately **1.010** over the section.

Thus the reported “1.23, then 1.01” is entirely noise-compatible, but it is **also compatible with a short correctly decoded page fragment**. The fall alone is not an independent rejection of a page-local key.

**(b) Control.** **Yes.** The plant began at the assumed origin, used no burn-in, and did not change keys across the scored interval.

**(c) Exact rerun.**

1. First rerun all original seeds at **every page start**, scoring within that page only.
2. For a bounded origin/burn-in closure, test:
   - ciphertext origin \(a=0\ldots63\) within each page, retaining starts with at least 120 available runes;
   - burn-in \(b=0\ldots1023\);
   - windows of length \(\min(300,L_j-a)\);
   - the skip rules from Gap 1.
3. Plant independent adjacent-page seeds, a nonzero origin, and burn-ins such as 37 and 1,023.
4. Threshold the full adaptive search by its own max-null distribution. Validate only within a continuation governed by the same planted/keyed page model.

Those bounds are explicit assumptions. They do not exclude origins after rune 63 or burn-in above 1,023.

**(d) Cost.**

- Page-start-only coverage: at most
  \[
  G\times4\times N\approx1.36\times10^{11}
  \]
  symbol evaluations before skip states.
- The full bounded origin/burn-in grid multiplies that by up to \(64\times1024\): approximately **\(8.9\times10^{15}\)** evaluations before skip states.
- On the 22 named seeds, the same box is approximately **\(7.5\times10^{10}\)** evaluations per generator/recipe set of that size.

**Recommendation:** run the page-start repair broadly; run the origin/burn-in box first on a frozen, evidence-motivated seed registry. That restricted run closes only that registry, not the entire original seed space.

### Gap 3: The true seed may simply be absent

**(a) Mechanism.** This is not score dilution: the true candidate was never evaluated, so all evaluated candidates can remain at noise.

The nominal searched fractions of a 32-bit seed space are:

- Perl/glibc: \(2^{20}/2^{32}=1/4096\).
- Python: \(2^{18}/2^{32}=1/16384\).

Unix timestamps contemporary with the material are far outside those low-seed ranges. Python integer seeds can also exceed 32 bits; no finite low-integer sweep covers arbitrary Python seeds.

**(b) Control.** **Yes.** Seed 777777 was intentionally placed inside its local control sweep. This tests recovery when present, not whether the real seed-selection model is represented.

**(c) Exact rerun.**

- Freeze a registry of authenticated release/publication timestamps before scanning.
- Search every integer second within **±7 days** of each timestamp: \(1,209,601\) seeds per nonoverlapping interval.
- Apply each generator’s actual seed conversion, including its effective integer width.
- Use page starts and the skip-aware engine; report any additional burn-in coverage separately.
- Plant seeds from the high-valued timestamp intervals, not just low integers.
- Use the complete max-null language-score threshold.
- If a full effective 32-bit sweep is undertaken, state exactly which generator/API it closes. It does not close arbitrary Python integer/string seeding.

**(d) Cost.** One timestamp interval, one generator/recipe, four forms, full-page coverage:
\[
1{,}209{,}601\times4\times12{,}956\approx6.27\times10^{10}
\]
symbol evaluations before skip states.

A full 32-bit sweep costs approximately
\[
2^{32}\times4\times12{,}956\approx2.23\times10^{14}
\]
per generator/recipe, again before skips, origins and null calibration.

### Gap 4: A different stream-reduction wrapper can produce the same fingerprint but a different keystream

**(a) Mechanism.** The tested APIs do not cover every natural way to obtain 28 symbols. For example:

1. draw a value in \(0\ldots28\);
2. reject 28;
3. retain \(0\ldots27\).

This produces a flat mod-28 key, but does **not** produce the same stream as directly drawing/modding by 28. Rejections change the underlying generator position.

The expected number of accepted symbols before the first rejection is 28. If only that initial fragment aligns with a direct-reduction scan, its contribution to 300-symbol IoC is negligible. The probability of no rejection in 300 initial draws is
\[
(28/29)^{300}\approx2.7\times10^{-5}.
\]

Python’s own `randrange` rejection machinery is already part of its specified recipe; that is **not** an omitted feature merely because it uses rejection internally.

**(b) Control.** **Yes.** The plant used the same direct recipe as the scanner. It did not contain an alternative wrapper. Bit-exact validation of drand48/libc cannot establish that the unknown author used the same wrapper.

**(c) Exact rerun.**

- Add two explicit wrappers around each tested 29-valued stream:
  - reject 28, retain 0–27;
  - reject 0, subtract one from retained 1–28.
- Apply the resulting key to the declared mod-28 chain, with the same explicit zero-event treatment as above.
- Plant each wrapper, including a seed with an early rejection.
- Search the original seed set first, page-locally and skip-aware.
- Use the full-search language-score max-null threshold.

This closes those two wrappers, not arbitrary output discards or plaintext-reactive rejection.

**(d) Cost.** Two additional stream recipes, with an average **29/28 underlying draws per accepted symbol**. Apart from alignment, cost is approximately two additional original-sized chain scans.

**Not worth rerunning for T3**

- **A giant Cartesian product of all 32-bit seeds, arbitrary offsets, arbitrary burns and arbitrary skips.** The cost is prohibitive, and unrestricted choices undermine discrimination. Run the well-supported page/skip repair before adding dimensions.
- **More broad raw mod-29 PRNG sweeps without a doublet-suppression mechanism.** An ordinary uniform pad predicts about 446 doublets, not 86. The deficit is roughly 17 binomial standard deviations descriptively; raw uniform-pad models are a poor fingerprint match.
- **Repeating the existing no-skip drand48 plant.** It already established its narrow claim. Add missing features and generator recipes.
- **Another fixed 1.25 cutoff after expanding the search.** That is not a valid rerun.
- **Unconstrained “discard outputs until plaintext looks good.”** This is an overfitting engine, not a specified PRNG hypothesis.
- **Treating whole-section decay as confirmation against page-local keys.** Use an in-page continuation instead.

### Ranked summary

1. **Page-local, skip-tolerant chain testing** is the highest-priority repair across all three tests: the chain domain matches the fingerprint; page changes and irregular F-skips match solved precedent.
2. **T2’s tokenization lattice and explicit rune-sequence direction/polarity coverage** are next. A genuine known-text key can be completely absent from a canonical rigid scan.
3. **T3’s page-start coverage and zero-step consumption rules** are stronger priorities than enlarging its low-seed interval. Its reported whole-section decay does not resolve page-local candidates.
4. **T3 timestamp seeds and small, explicit reduction wrappers** are justified bounded extensions, but the evidence does not specifically identify a PRNG.
5. **Long unconstrained periodic keys, unrestricted edits and enormous seed/offset products** are poor investments: they face either insufficient information, severe selection penalties or prohibitive cost.

None of the three negatives currently excludes the combined model **“page-local key, differential arithmetic, irregular exceptional events.”** That is a coverage conclusion—not evidence that this combined model is actually the cipher.
