---
id: B23
title: Bigram-refined column shifts for short pages and periods 14-40
status: open
claimed_by: ""
rank: 5
ledger: [E0030]
---

# B23 Bigram-refined column shifts (page-local periodic keys, beyond E0030's region)

## Why
E0030's unigram best-shift detector verifies page-local periodic keys only up to L 13 on 217 runes, L 5
on 137 runes and raw L 3 on 76 runes. Past that, columns hold < ~10 symbols and unigram fits overfit
(the real best page, p55 L 13, decrypts to frequent letters with no words). Adjacent columns are adjacent
plaintext letters, so the bigram term carries information that the unigram score ignores.

## Test design
1. Import E0030's ScoreView and SearchPage. For each (page, view, L) keep the top few masks by unigram z,
   then hill-climb the L column shifts on unigram + bigram LLR of the decryption (a few restarts).
   Standardise per page against surrogates, as E0030 does.
2. Periods 14-40 on pages >= 217 runes; periods 5-20 on the 13 pages of < 217 runes (8 of them 137-216).
3. Tier 1 on p25, p3, p14, p55 layouts plus one 159-201 rune page; tier 2 = 999 E0027 surrogates with the
   hill climb inside (budget: the climb must stay under ~1 s per page-view, or reduce surrogates and say how
   many).

## Notes
The climb makes the score search-dependent: fix restarts and seeds so surrogates run the identical search.
