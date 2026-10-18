# 02 gpt-6-astra / kickoff-cryptanalyst

- id: 20261018T173544-e8a3edaa
- time: 2026-10-18T17:39:52Z
- branch: claude/stoic-feynman-g6muzj
- model: gpt-6-astra, mode standard, effort medium, max-output 16000
- status: completed
- usage: input_tokens 3491, output_tokens 9800, reasoning_tokens 6214, total_tokens 13291

## Prompt

You are a senior cryptanalyst reviewing an unsolved 2014 hand-set cipher text. Below is the complete
evidence file. Give 12 concrete, testable constructions (cipher plus key source plus handling of the
F-skips) that would produce exactly this fingerprint: flat IoC near 1.00 in every section, uniform
steps 1..28, no periodicity, no depth between sections, and only 86 doublets where about 446 are
expected. For each construction give: (a) the mechanism in one or two sentences, precise enough to
code; (b) why it yields the doublet deficit and nothing else; (c) the cheapest falsifying test on
this data, with the statistic to compute and the value that would refute it; (d) which excluded
ledger family it is closest to and what is new. Prefer constructions that explain WHY the deficit
is 86 and not 0. Do not repeat the excluded families unless you name a specific gap in their
coverage. Answer in a numbered list, no preamble, no questions back.

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

1. **Independent rare-zero instructions from a hash-expanded key.**  
   **(a) Mechanism.** Use the decoded page-56 hash as seed; expand it with HMAC-SHA-512 over separate labels for section, purpose, and counter, using rejection sampling for bounded integers. At each keyed position, draw \(u\in[0,148]\): require step 0 when \(u=0\), and otherwise allow steps 1–28.

   **Common coding and F-skip assumptions for constructions below:** These are testable generators, **not verified explanations of the actual ciphertext**: the evidence supplies summaries, not the rune stream or skip positions. To make constrained-output proposals genuinely reversible, losslessly compress the plaintext, pad it to an integer \(x<M\), add a separately expanded key integer modulo \(M\), and unrank into the \(M\) allowed ciphertext strings; decoding reverses this. Preserve the supplied boundary map. Assume a sparse auxiliary skip mask \(S\), searched rather than freely fitted: a skip emits literal plaintext/ciphertext F, consumes neither a gate instruction nor a payload digit, but sets the visible accumulator to 0. Declare the permitted skip budget before testing.

   **(b) Fingerprint.** Away from skips, \(q=P(s=0)=1/149\), giving 86.89 expected doublets—not a prediction that the realization must be exactly 86. Nonzero steps are exactly uniform. With \(L\) skipped adjacent positions, the approximate expectation becomes
   \[
   (12947-L)/149+L/29.
   \]
   This predicts no additional *large* anomaly, not literally no other statistical effect.

   **(c) Cheapest falsification.** Generate the gate sequence and count disagreements between its required zero/nonzero steps and the observed steps, excluding literal-skip edges. **Minimum disagreement over every admissible skip mask greater than 0 refutes this specified seed/model.** The raw sequence is needed to execute that test.

   **(d) Ledger proximity.** E0021/E0013. The gap is using hash material to define a constrained output alphabet and an enumerative cipher, rather than adding a hash-derived pad mod 29. The choice 149 is fitted to the observed rate, not independently justified.

2. **Occasional permission to use the full 29-symbol alphabet.**  
   **(a)** Use `DIVINITY` as the seed under the expansion convention in item 1. Independently mark one fifth of keyed positions “open”; closed positions allow only nonzero steps, while open positions allow all 29 steps. Use the reversible constrained-output codec and F handling above.

   **(b)** An open position repeats with probability \(1/29\), so \(q=1/145\), giving 89.29 expected doublets before skips. This explains leakage without making every exceptional instruction produce a doublet; conditional on being nonzero, every step still has probability \(1/28\).

   **(c)** Count doublets occurring at closed positions. **A minimum count greater than 0 over admissible skip masks refutes it.** As a secondary test, among \(m\) open positions, the doublet count must fit \(\mathrm{Binomial}(m,1/29)\); reject at exact two-sided \(p\le .001\), with skip-search selection included in calibration.

   **(d)** E0002/E0021. The keyword supplies a nonperiodic counter-expanded gate and payload pad, not a repeated Vigenère key; the new component is randomized alphabet relaxation.

3. **Renewal-scheduled zero steps with a refractory interval.**  
   **(a)** Seed from the comma-separated decimal entries of the page-15 square, in row-major order. Generate gaps \(G=7+X\), where \(P(X=k)=(142/143)^k/143\); use the stationary renewal initialization, force a zero at renewal positions, and allow only nonzero steps elsewhere. Apply item 1’s codec and F rule.

   **(b)** \(E[G]=149\), yielding about 86.89 doublets before skips, but never two scheduled zeros fewer than seven keyed positions apart. This removes close *zero-event pairs*, not ordinary lag-2 or lag-3 coincidences, which can arise from cancelling nonzero steps.

   **(c)** First compute the minimum separation between observed doublet events after admissible skip alignment. **Any pair separated by fewer than seven keyed positions, neither attributable to a skip, refutes it.** If that passes, compare the complete zero schedule against the seeded renewal schedule; any unavoidable mismatch refutes the specified key.

   **(d)** E0005/E0021. Renewal timing is neither an arithmetic sequence reduced mod 29 nor an additive hash pad. Its new, falsifiable feature is a short exclusion interval.

4. **An unbordered bit-pattern interrupter.**  
   **(a)** Seed from the concatenated decoded 2013 cookies. Read one gate bit per keyed position and force step 0 whenever the seven-bit window ending there is `1000000`; otherwise allow steps 1–28. Initialize each section with six independently generated gate bits, and use item 1’s codec/F handling.

   **(b)** The event probability is \(1/128\), giving 101.15 expected doublets before skips; 86 is an ordinary downward fluctuation, though this fits less closely than \(1/149\). Because `1000000` cannot overlap itself, it avoids the conspicuous runs of zeros that a “seven consecutive ones” trigger would produce.

   **(c)** **Two non-skip doublet events less than seven keyed positions apart refute it.** The stronger seed-specific test is zero-mask disagreement, with refutation at minimum disagreement \(>0\). Evaluate the total count against the pattern-occurrence distribution, not a binomial approximation.

   **(d)** E0003/E0021. The interrupter is a pattern in an expanded key bitstream, not a ciphertext rune or a short periodic keyword. This names a concrete gap rather than repeating generic interrupter searches.

5. **A key-collision interrupter.**  
   **(a)** Seed from the decimal representation of the smaller supplied 2012 prime factor. Generate independent uniform key tokens \(a_i\in[0,148]\), including an initial token; force zero iff \(a_i=a_{i-1}\), and otherwise allow nonzero steps. A literal F-skip leaves the token index unchanged but resets the visible accumulator as specified above.

   **(b)** Key-token collisions occur with probability \(1/149\). For independent uniform tokens, these adjacent equality indicators are themselves independent, so this has the same observable step distribution as item 1: approximately 87 accidental key-collision instructions, not plaintext doubled letters.

   **(c)** Compute
   \[
   T=\#\{i:\mathbf1[s_i=0]\ne\mathbf1[a_i=a_{i-1}]\}
   \]
   on non-skip keyed transitions. **Minimum \(T>0\) over permitted masks refutes the specified construction.** There is no ciphertext-only distributional test distinguishing it from item 1 when the seed is unknown.

   **(d)** E0022/E0021. The factor is neither written in base 29 nor used directly as an additive pad; it seeds a token-collision schedule. The equivalence to item 1 is an identifiability limitation, not independent evidence.

6. **Two independent clocks must coincide.**  
   **(a)** Seed two independent gate streams with the ASCII strings `1033` and `3301`, domain-separated by section. Draw \(a_i\in[0,10]\) and \(b_i\in[0,12]\); force zero exactly when both are 0, allowing nonzero steps otherwise. Seed the payload-rank pad with their concatenation and use the common F rule.

   **(b)** The coincidence probability is \(1/(11\cdot13)=1/143\), giving 90.54 expected doublets before skips. Neither clock is periodic: these are independently expanded random draws, not counters cycling through 11 and 13.

   **(c)** Compare observed zero positions with the intersection of the two generated schedules. **Any unavoidable false positive or false negative refutes it.** Marginal doublet counts alone cannot distinguish this mechanism from an independent rare-event gate.

   **(d)** E0005/E0019/E0021. The gap is a Boolean combination of two separately expanded key streams controlling the output alphabet. The parameters 11 and 13 are speculative; their product’s agreement with the rate is not a discovered clue.

7. **Ciphertext-feedback hashing chooses the forbidden transition.**  
   **(a)** Seed from the decoded page-56 hash. Before keyed position \(i\), hash the seed, section label, keyed index, and complete preceding ciphertext prefix; rejection-reduce the result to \(u_i\in[0,148]\), forcing zero iff \(u_i=0\). Enumerate the resulting prefix tree for reversible encoding; skips emit F, update the prefix, and do not advance \(i\).

   **(b)** Under the pseudorandom-function heuristic, fresh prefix inputs give a zero probability of \(1/149\), with uniform nonzero alternatives. The running state destroys a fixed keystream interpretation without producing a simple lag-autokey signature.

   **(c)** This has a particularly cheap necessary test: evaluate the hash along the **observed** ciphertext prefix and compare its gate with each step. **Minimum gate disagreement \(>0\) over admissible masks refutes it.** No plaintext recovery is required.

   **(d)** E0007/E0021. The specific gap is nonlinear, full-prefix cryptographic feedback, rather than linear autokey at tested lags or a ciphertext-independent hash pad. This is computationally cumbersome to encode, which lowers its historical plausibility.

8. **Whole-word relaxation of the no-repeat rule.**  
   **(a)** Seed from `FIRFUMFERENFE`. Independently designate each ciphertext word open with probability \(1/5\); all keyed transitions whose destination lies in an open word allow steps 0–28, while other transitions allow 1–28. Use section-separated expansion, the common codec, and the common F rule.

   **(b)** The marginal zero probability is \(1/145\), including both within-word and word-entry transitions. It therefore does not automatically predict suppression only inside words, but it **does** predict modest clustering of doublets within the same words—a higher-order feature not resolved by the supplied summaries.

   **(c)** First count doublets in seeded closed words: **minimum count \(>0\) refutes it.** A seed-free secondary statistic is
   \[
   W=\sum_w {D_w\choose2},
   \]
   where \(D_w\) counts doublet events assigned to word \(w\). Reject if its model-calibrated two-sided \(p\le .001\), using the actual word lengths and skip procedure.

   **(d)** E0009/E0015. Words select an alphabet regime, not a shift or reset to a shared key position. The payload key continues across boundaries, so the tested same-position depth mechanism is absent.

9. **A persistent two-state alphabet switch.**  
   **(a)** Seed from `CIRCUMFERENCE`. Generate a stationary Markov gate with \(P(\text{closed}\to\text{open})=.05\) and \(P(\text{open}\to\text{closed})=.20\); open positions allow all steps, closed positions only nonzero steps. Use separately expanded payload encryption and the common F rule.

   **(b)** The stationary open fraction is \(1/5\), hence \(q=1/145\). The gate is aperiodic and creates diffuse local clustering rather than word-, line-, or period-aligned repetition; its extra short-lag coincidence effects can remain below the reported tests’ resolution.

   **(c)** Seed-specific falsification is again **any unavoidable doublet at a closed position**. A source-free test is the zero-event autocovariance
   \[
   A_h=\sum_i(Z_i-\bar Z)(Z_{i+h}-\bar Z),\quad h=1,\ldots,20.
   \]
   Reject at a simulated, jointly calibrated \(p\le .001\); the latent-state correlation decays as \(0.75^h\).

   **(d)** E0019/E0015. The untested component is a hidden, persistent alphabet regime, not another ordinary PRNG pad or a boundary reset.

10. **At most one zero instruction per 32-position packet.**  
    **(a)** Seed from the grid’s full 256 decoded bytes. Divide keyed positions into 32-position packets with a seeded random initial phase; each full packet is selected with probability \(32/149\), and a selected packet gets exactly one uniformly located forced zero. For a terminal partial packet of length \(r\), use selection probability \(r/149\); otherwise allow only nonzero steps, with common F handling.

    **(b)** Every position has marginal zero probability \(1/149\), but zero events repel one another within packets. This produces no periodic mean step distribution or shared key position; a specialized packet-occupancy test can nevertheless detect the structure.

    **(c)** For each allowed phase and skip alignment, compute
    \[
    B=\#\{\text{packets containing at least two non-skip doublets}\}.
    \]
    **Minimum \(B>0\) refutes the packet construction even before testing the seed.** The seeded selected-packet/location schedule supplies a stronger exact test.

    **(d)** E0023/E0015. The grid seeds packet occupancy and rank encryption rather than supplying repeated bytes or a resetting pad. The 32-column geometry motivates the packet size, although it does not establish it.

11. **A random global quota, then uniformly scattered zero instructions.**  
    **(a)** Seed from the larger supplied 2012 prime factor. Draw a total visible-doublet quota \(D\) from a Poisson distribution with mean \(12947/149\), rejecting infeasible values; uniformly rank-code among complete ciphertexts satisfying that quota, the section breaks, and the literal-F mask. Use independent domain separation for the quota and encrypted rank.

    **(b)** The expected count is 86.89, and 86 is near the mode. Uniform placement prevents periodicity or a preferred plaintext position; uniform rune-label symmetry preserves flat marginal rune counts and equal nonzero-step probabilities. Unlike item 1, the count is chosen first rather than emerging from local Bernoulli trials.

    **(c)** Generate the seeded quota: **\(D_{\text{seed}}\ne86\) immediately refutes this specified key.** If it equals 86, test the section-count vector and zero spacings against the exact constrained ensemble, rejecting at jointly calibrated \(p\le .001\).

    **(d)** E0022/E0021. The gap is global combinatorial allocation of a random exception budget. This is not evidence for the factor: with an unknown seed, its observable distribution is extremely close to the independent-gate alternatives.

12. **A fixed-budget constrained cipher that explains exactly 86—by construction.**  
    **(a)** Set the visible-doublet budget to
    \[
    D=\left\lfloor N/149\right\rfloor,\qquad N=12947,
    \]
    hence \(D=86\). Seed the rank-encryption pad from the grid bytes plus the row-major page-15 square, and enumerate exactly those strings having 86 doublets, respecting section boundaries and the F-skip mask; a dynamic program over position, previous rune, and remaining budget implements ranking/unranking.

    **(b)** This yields exactly 86 rather than merely an expectation near it. Uniform enumeration gives approximately uniform placement and nonzero steps, with only the weak dependence imposed by a fixed total; skipped Fs are included in the budget, not added afterward.

    **(c)** The count test is **\(D_{\rm observed}\ne\lfloor N/149\rfloor\)**, which this file passes tautologically. On these data, test section allocation and zero spacings against the constrained ensemble at \(p\le .001\), then decrypt with planted-control-calibrated language scoring. **The count itself supplies no independent validation because 149 was selected after seeing it.**

    **(d)** E0023/E0021. Global constrained coding was not covered by raw/chain grid pads or ordinary hash pads. This is the clearest engineering counterexample to uniqueness, but not a strong historical hypothesis: without an independently sourced budget rule, “explains exactly 86” means fitting the observation, not explaining its origin.
