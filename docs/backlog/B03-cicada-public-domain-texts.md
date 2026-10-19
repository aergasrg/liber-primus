---
id: B03
title: Public-domain Cicada texts as running keys
status: done
claimed_by: claude/charming-babbage-raidxt
rank: 3
ledger: [E0008, E0035]
---

# B03 Public-domain Cicada texts as running keys

## Why
Cicada used Liber AL vel Legis (2013 book code), the Britannica 1911 'Cicada' article (2012) and Blake's Marriage of Heaven and Hell (2012). None has been scanned as a running key.

## Test design
1. Fetch by script into data/texts/ (Project Gutenberg / Wikisource; public domain). Never commit the texts.
2. Transliterate with lp.gematria.LatinToRunes; keep word boundaries for later word-level variants.
3. Raw (LLR via FFT) and chain (IoC) scans at every offset, both signs, both directions.
4. Use the B01 engine if it exists; otherwise record skips_handled: no and leave the B01 rerun open.

## Notes
Planted control from the same text with F-skips; null from an unrelated public-domain text of the same length.

## Outcome
Done in E0035 (negative). Liber AL vel Legis (Wikisource), the EB1911 "Cicada" article and Blake's Marriage of Heaven and Hell, page-local, skip-tolerant, 32 forms, 55 pages: best standardised 5.14 / 5.21 / 5.02 against a 9.71 threshold; planted controls 100/100 on pages of 141+ runes. Open: the six short pages, and `lp.runningkey.Trace` raises StopIteration on unit28z2 plants (diagnostic only).
