---
id: B14
title: Self-addressing walks through LP's own plain pages
status: open
claimed_by: ""
rank: 14
ledger: []
---

# B14 Self-addressing walks through LP's own plain pages

## Why
Every solved key came from the book's plain pages, and the 2016 hint says the words are the map
and their numbers the direction. A key that walks through the plain pages with an address updated by
the book's own numbers is aperiodic, flat, and defeats every fixed-offset running-key scan in the
ledger (E0008, E0012, E0024). The council's designer call
(docs/council/2026-10-18/03-gpt-6-astra-kickoff-designer.md, items 2, 4, 5, 6, 7, 8, 9) gave exact
update rules. B02 covers plaintext-reactive pointers in general; this item is the book-driven and
number-steered walks with exact rules, over LP's own plain pages only.

## Test design
1. Book W = words (and B = runes) of Some Wisdom, The Loss of Divinity, An Instruction, Parable in
   order, headings and numerals excluded; V(w) = Gematria Primus prime sum of word w; G(r) = prime of
   rune r; section start address a_h in {0,3,8,15,23,27,33,40,54} (first page number) and also 0.
2. Key value x_j from the word or rune at address z_j (x = V(W_z) mod 29 and mod 28; also G(B_z)).
   Address rules, each a separate variant:
   - book-driven: z <- z + 1 + G(B_z) + j;
   - plaintext-driven: z <- z + 1 + G(p_j) + j (B02's rule, included for the shared control);
   - word-driven: at each plaintext word end, z <- z + |w| V(w) + prime(m) for the m-th word;
   - number-steered: z <- z + D_(j mod 16) + prime(j+1) with D = the page-15 square's cells minus 3301
     (exact values in docs/LEADS.md); z <- z + 1 + g_(j mod 256) + j with g = the 256 grid bytes;
     z <- z + M_r + j with M = the primes 73..1223 and r <- r + 1 + c_(i-1);
   - stencil: z_j = 1033 j + j^2 + 3301 a_h, x_j = sum of r V(W_(z+r-1)) for r = 1..5.
3. Apply x_j raw (c - x mod 29, both signs) and in chain form (u - x mod 28). F-skips: a ciphertext F
   that neither advances j nor the address; branch at every F (the B01 engine).
4. Detector: unigram LLR and bigram gain on the first 300 runes of each section; full-section recheck
   of anything above the ceiling.
5. Control: plant each rule over solved plaintext with the same book and recover it. Null: the same
   rules over a shuffled book, best-of-variants ceiling; count every variant for multiple testing.

## Notes
Keep the rule list fixed before running; do not tune rules to the score. Overlaps B02 (rule 2b) and
B11 (page/line/word addressing); cite both in the ledger entry.
