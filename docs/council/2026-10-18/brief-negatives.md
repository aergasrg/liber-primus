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
