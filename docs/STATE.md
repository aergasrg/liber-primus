# State of knowledge

Numbers verified from relikd's transcription (session one, 17 Oct 2026; re-verified by the gate on
18 Oct 2026). Experiments and their outcomes live in the ledger (docs/LEDGER.md); open ideas in
docs/BACKLOG.md; unused clues in docs/LEADS.md.

## Gematria Primus

| idx | rune | latin | prime | idx | rune | latin | prime | idx | rune | latin | prime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | ᚠ | F | 2 | 10 | ᛁ | I | 31 | 20 | ᛚ | L | 73 |
| 1 | ᚢ | U/V | 3 | 11 | ᛄ | J | 37 | 21 | ᛝ | NG/ING | 79 |
| 2 | ᚦ | TH | 5 | 12 | ᛇ | EO | 41 | 22 | ᛟ | OE | 83 |
| 3 | ᚩ | O | 7 | 13 | ᛈ | P | 43 | 23 | ᛞ | D | 89 |
| 4 | ᚱ | R | 11 | 14 | ᛉ | X | 47 | 24 | ᚪ | A | 97 |
| 5 | ᚳ | C/K | 13 | 15 | ᛋ | S/Z | 53 | 25 | ᚫ | AE | 101 |
| 6 | ᚷ | G | 17 | 16 | ᛏ | T | 59 | 26 | ᚣ | Y | 103 |
| 7 | ᚹ | W | 19 | 17 | ᛒ | B | 61 | 27 | ᛡ | IA/IO | 107 |
| 8 | ᚻ | H | 23 | 18 | ᛖ | E | 67 | 28 | ᛠ | EA | 109 |
| 9 | ᚾ | N | 29 | 19 | ᛗ | M | 71 | | | | |

## Solved sections (relikd file names in brackets)

| Section | Method |
| --- | --- |
| A Warning [0_warning] | Atbash |
| Welcome [0_welcome] | Vigenere DIVINITY; the 4,5,6,7,10,11,14,18,20,21,25th ciphertext F pass through without consuming key (11 F-skips) |
| Some Wisdom [0_wisdom] | plain; ends in a word/number square |
| Koan 1 [0_koan_1] | Atbash then +3 |
| The Loss of Divinity [0_loss_of_divinity] | plain |
| Koan 2 [jpg107-167] | Vigenere FIRFUMFERENFE (= CIRCUMFERENCE with C->F), 2 F-skips |
| An Instruction [jpg229] | plain; 5x5 square, rows sum 3301 |
| An End [p56_an_end] | subtract (prime_n - 1), one F-skip (the 4th F) |
| Parable [p57_parable] | plain |

Every key came from the book's own plain pages. Every keyed solved section uses F-skips.
The gate reproduces Warning, Welcome, Koan 1 and An End exactly; Koan 2 is not in the gate yet.

## Unsolved: 9 sections, 12,956 runes, 2,896 words

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

Word count: the session-one brief said 2,921, but `lp.data` gives 2,896, and the brief's own mean word
length (4.47 = 12,956 / 2,896) matches 2,896. The gate pins 2,896.

- IoC 0.98-1.00 in every section (random 1.0, English in runes ~1.78).
- **The one fingerprint:** 86 doublets in 12,947 adjacent pairs (0.66%; random 3.45%, ~446 expected).
- Step histogram c_i - c_(i-1) mod 29, steps 0..28:
  `86, 459, 504, 440, 438, 446, 430, 470, 426, 510, 497, 454, 449, 503, 474, 469, 448, 404, 433, 474, 467, 462, 421, 486, 467, 467, 457, 475, 431`
- Steps 1-28 are uniform and independent of the previous rune; lag-2 and lag-3 coincidences are normal.
- Doublets fall on all runes, inside words (0.63%) and across gaps (0.80%), and are real glyphs on the images.
- Doublet suppression appears in plain reading order, so no transposition sits on top of the chain.
- No periodicity up to 300 per section or 600 overall; no shared keystream between sections at overlaps of 600+.
- Mean word length 4.47 runes (solved pages 4.03 in session one; 4.07 over all seven relikd solved files
  with this loader); two-rune words 15.5%.
- One repeated 6-gram, DJUBEI, at corpus positions 6555 and 12950 (0-based, sections concatenated in order).

## Working model

Only known model that fits: a **chain cipher**, c_i = c_(i-1) + s_i with s_i in 1..28 from a flat,
aperiodic key (steps of 0 would be the rare doublets). So the problem is finding the key source.
In `lp.ciphers` the chain unit is u_i = s_i - 1 (0..27) for non-doublet steps.

## Cicada hints

- 2016 signed message: Liber Primus is the way; its words are the map, their meaning is the road, and
  their numbers are the direction.
- 2017 signed message: beware false paths; always verify the PGP signature from 7A35090F.

## Detector reference values (300-rune windows unless noted)

| Detector | English (keyed control) | Random | Note |
| --- | --- | --- | --- |
| IoC mod 29 (raw) | ~1.78-1.93 | 1.00 +- 0.03 | max over 10^6 trials reaches ~1.20-1.25 |
| IoC mod 28 (chain) | ~1.81 | 1.00 | |
| Unigram LLR / rune | +0.40 | -0.6 to -0.84 | raw form only |
| Bigram gain / rune | ~+0.5 | ~0 | |
