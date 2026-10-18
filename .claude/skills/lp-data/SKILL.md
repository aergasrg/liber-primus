---
name: lp-data
description: How to load and interpret the Liber Primus transcription in this repo - file format, lp.data conventions, cipher conventions, and the known pitfalls that have produced false hits. Use before writing any code that reads LP data or scores candidates.
---

# lp-data

## Getting the data

`bash scripts/fetch_data.sh` downloads relikd's transcription into `data/` (gitignored):
`data/pages/<name>.txt` for the 9 unsolved sections (p0-2 ... p54-55), the solved cipher pages
(0_warning, 0_welcome, 0_wisdom, 0_koan_1, 0_loss_of_divinity, p56_an_end, p57_parable, jpg107-167 =
Koan 2, jpg229 = An Instruction), their `solved_*.txt` plaintexts, and `data/baseline-rune-words.txt`
(English corpus in runes, one word per line). Public-domain texts go in `data/texts/`, fetched by script.

## Format

Runes; `•` word break; `⁘` sentence end; `⁚` colon; `⁜` heading end; blank line = page break
(unreliable, see pitfalls). Digits and Latin letters are not runes (digits end a word). A line break
does NOT end a word: words wrap across lines.

## Loading

```python
from lp.data import LoadSection, LoadAllUnsolved, Words, SolvedPlaintext, UnsolvedNames
Section = LoadSection("p54-55")
Section["Runes"]          # rune indices 0..28
Section["WordId"], Section["PosInWord"], Section["SentenceId"], Section["PosInSentence"]
Section["LineId"], Section["PosInLine"], Section["PageId"], Section["PosInPage"], Section["WordLen"]
```

Corpus positions (e.g. DJUBEI at 6555 and 12950) are 0-based over the 9 sections concatenated in
`UnsolvedNames` order.

## Conventions (lp.ciphers)

- Vigenere decrypt p = c - k; Beaufort p = k - c; Atbash p = 28 - c; all mod 29.
- F-skip: a ciphertext F that passes through unchanged and does NOT consume key. Specified as 1-based
  ordinals of ciphertext Fs (Welcome: 4,5,6,7,10,11,14,18,20,21,25).
- Chain form: s_i = c_i - c_(i-1) mod 29; chain unit u_i = s_i - 1 for s_i != 0 (doublets dropped);
  keyed chain u_i = (p_i % 28 + k_i) % 28.
- Latin to runes: `LatinToRunes` (Q,K->C; V->U; Z->S; longest match ING/NG, TH, EO, OE, AE, IA/IO, EA).

## Pitfalls

- Blank lines are not reliable page breaks: p3-7, p15-22, p33-39 and p40-53 parse to the wrong
  page count. Use line counts or the page images.
- IoC maxima over millions of trials on 300-rune windows reach ~1.2-1.25 by chance; always re-score
  top hits on the whole section.
- Binomial tails with p = 1/29 are skewed; use permutation nulls, not normal z.
- Log-likelihood scoring needs letter identities (raw form only); the chain form needs IoC, since
  the step-to-letter mapping is unknown.
- A 2025 wiki note says every page hides OutGuess data; controlled runs show that is random LSB noise.
- The word count is 2,896 (the session-one brief's 2,921 was inconsistent with its own mean length).
- Running-key scans with rigid alignment (FFT) silently fail if the key skips at an F; see B01.
