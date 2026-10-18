You are a puzzle designer working in the style of Cicada 3301 (2012-2014): self-referential keys
taken from the book's own plain pages, primes and gematria, Old English runes, book codes, hand
checkable arithmetic, a taste for 'the words are the map, their meaning the road, their numbers the
direction'. Below is the complete evidence file for the unsolved pages. Give 12 concrete, testable
constructions a designer of this school would plausibly have used that produce exactly this
fingerprint: flat IoC near 1.00, uniform steps 1..28, no periodicity, no depth, only 86 doublets
where about 446 are expected. For each: (a) the designer's rule in one or two sentences, precise
enough to code, including what the F-skips and the doublets mean under that rule; (b) where in the
book or the earlier puzzles the key material would come from, with exact candidates; (c) the
cheapest falsifying test on this data, with the statistic and the refuting value; (d) which excluded
ledger family it is closest to and what is new. Favour rules that are hand-executable with the
printed material and that make the 86 doublets meaningful rather than accidental. Answer in a
numbered list, no preamble, no questions back.

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
