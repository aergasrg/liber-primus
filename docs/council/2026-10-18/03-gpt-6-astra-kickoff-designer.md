# 03 gpt-6-astra / kickoff-designer

- id: 20261018T173548-25697a22
- time: 2026-10-18T17:39:53Z
- branch: claude/stoic-feynman-g6muzj
- model: gpt-6-astra, mode standard, effort medium, max-output 16000
- status: completed
- usage: input_tokens 3560, output_tokens 10793, reasoning_tokens 6178, total_tokens 14353

## Prompt

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

## Reply

1. **Rare-symbol escape with a prime-addressed running book.**

   **(a) Rule.** Assume ordinary English plaintext, the printed word boundaries, and section-initial state \(c_{-1}=0\). These are testable constructions—not verified fits: the brief supplies aggregate statistics, not the rune stream, full grid, or source-page transcriptions needed to execute them.

   Use the following **shared codec** for constructions 1–9, 11, and 12. A key-source integer \(x_j\), indexed by consumed plaintext runes, selects
   \[
   R=(11,12,14,22)=(J,EO,X,OE),\quad
   q_j=R[x_j\bmod4],\quad t_j=\lfloor x_j/4\rfloor\bmod28.
   \]
   Encode
   \[
   s_j=\begin{cases}
   0,&p_j=q_j,\\
   1+\bigl(r_{q_j}(p_j)+t_j\bmod28\bigr),&p_j\ne q_j,
   \end{cases}
   \qquad c_i=c_{i-1}+s_j\pmod{29},
   \]
   where \(r_q(p)=p-\mathbf1[p>q]\). Thus **a doublet identifies a key-selected rare plaintext rune**, not one fixed rune or a doubled letter. Unlike simply excluding zero from a mod-29 pad, this actually represents all 29 plaintext symbols.

   For a concrete shared **F-skip hypothesis**, number words from 1 within each section: a word-initial plaintext F in a prime-numbered word is emitted literally as ciphertext 0 without advancing the key or updating its internal state; the ciphertext accumulator nevertheless becomes 0. Decoding branches at eligible ciphertext F’s and checks the forward rule. This predicts a particular irregular skip set; it is not claimed to reproduce the solved pages’ skip masks. A skipped F can itself create a doublet only when preceded by ciphertext F.

   Let \(W\) be the words of **Some Wisdom, The Loss of Divinity, An Instruction, Parable**, in that order, excluding headings, artwork, and Arabic numerals; let \(V(w)\) be its Gematria Primus prime sum. Put
   \[
   a_h=(0,3,8,15,23,27,33,40,54)_h,\quad
   u_j=(a_h+j(j+1)/2)\bmod |W|,
   \]
   \[
   x_j=V(W_{u_j})+29V(W_{(u_j+\pi_{j+1})\bmod|W|}),
   \]
   where \(\pi_n\) is the \(n\)th prime.

   **(b) Key material.** Exactly those four plain pages, the supplied GP table, primes, and each section’s first page number.

   **(c) Cheapest falsifying test.** Decode the first 300 runes of each section. Use the supplied unigram LLR per rune, maximized only over legal F-skip branches. **Operational rejection: pooled LLR \(\le0\)**, provided same-length English plants encrypted with this exact construction recover at LLR \(\ge+0.20\). Apply this controlled screening test to every construction below unless a cheaper structural test is specified. Passing is not confirmation: full-length decoding must also reproduce the 86 doublets, their profiles, step uniformity, and absence of detectable periods. The rare-symbol rates must be measured from independent plain text, not fitted to 86.

   **(d) Ledger proximity.** E0008/E0012/E0024 and E0005/E0006/E0017. New: nonlinear book addressing, an explicitly invertible rare-symbol escape, and a fixed plaintext-conditioned skip rule—not another rigid running-key alignment.

2. **Gematria-driven walk through the plain runes.**

   **(a) Rule.** Let \(B\) be the rune sequence obtained by concatenating the same four plain pages under the conventions above, and \(G(r)\) the supplied prime value. Start \(z_0=a_h\bmod|B|\); output
   \[
   x_j=G(B_{z_j})+29G(B_{(z_j+1)\bmod|B|}),
   \]
   then advance
   \[
   z_{j+1}=(z_j+1+G(B_{z_j})+j)\bmod|B|.
   \]
   Use the shared codec and F rule: doublets disclose the selected member of \(R\), while an F-skip leaves \(z\) and \(j\) unchanged.

   **(b) Key material.** The four named plain pages and their printed GP prime values. The rule literalizes “their numbers [are] the direction”: a rune’s number controls the next address.

   **(c) Cheapest falsifying test.** Generate the key without decrypting and tabulate the resulting \((q_j,t_j)\) distribution. Encrypt independent solved plaintext, preserving the target section lengths, and measure the 28-bin nonzero-step chi-square. **Reject if the observed histogram falls outside the central 99.9% of the construction’s planted distribution.** This can eliminate a strongly biased book walk before any language search; otherwise apply the LLR screen.

   **(d) Ledger proximity.** E0008 and E0005/E0006/E0017. New: the source text determines its own successive addresses, with a nonresetting counter preventing a simple fixed walk around a short cycle.

3. **Page–line–word prime book code.**

   **(a) Rule.** Preserve the four source pages as separate pages and preserve their printed text lines; discard empty lines. At consumed position \(j\), select page, line, and word by
   \[
   P=\pi_{j+a_h+1}\bmod4,\quad
   L=\pi_{2j+a_h+1}\bmod n_P,\quad
   K=\pi_{3j+a_h+1}\bmod n_{P,L},
   \]
   using zero-based lists; for the selected word \(w\), set
   \[
   x_j=V(w)+29|w|+841\,w_0.
   \]
   Use the shared codec and F rule.

   **(b) Key material.** Exact page candidates: Some Wisdom, The Loss of Divinity, An Instruction, Parable. The lineation is key material, not merely a transcription convenience.

   **(c) Cheapest falsifying test.** Run the 300-rune LLR screen with these exact addresses and no offset search. **Refuting screening value: pooled LLR \(\le0\)** with successful controls. A failure must not be “repaired” by freely changing line wrapping or whether a heading counts; those would be separately registered hypotheses.

   **(d) Ledger proximity.** E0026 and E0008/E0012/E0024; directly addresses B11. New: hierarchical local addressing rather than a global word index or rigid rune offset.

4. **Plaintext-reactive book walk.**

   **(a) Rule.** Start \(z_0=a_h\bmod|W|\); set
   \[
   x_j=V(W_{z_j})+29V(W_{(z_j+1)\bmod|W|}),
   \]
   and, after encoding or decoding a non-skipped rune \(p_j\), update
   \[
   z_{j+1}=(z_j+1+G(p_j)+j)\bmod|W|.
   \]
   Doublets reveal \(q_j\) and therefore also determine the following address update; F-skips emit literal F but do not advance the walk.

   **(b) Key material.** The same four-page word book, GP prime values, and section-start page number. No additional keyword is introduced.

   **(c) Cheapest falsifying test.** Sequentially decode 300 runes per section, branching only at legal F-skips. **Reject at pooled LLR \(\le0\)** if the controls pass. Also verify round-trip reproduction: **one mismatched ciphertext rune** is a hard rejection of a proposed plaintext/skip path.

   **(d) Ledger proximity.** E0007 and E0008; B02. New: plaintext selects a nonlinear external book address. It is not additive plaintext autokey at lag 1–3, although that is its nearest conceptual relative.

5. **Word meaning carried by word number: word-reactive routing.**

   **(a) Rule.** Keep a book address \(z\), initially \(a_h\bmod|W|\); at each consumed rune use
   \[
   x_j=V(W_{(z+j)\bmod|W|})+29V(W_{(z+j+1)\bmod|W|}).
   \]
   At the end of plaintext word \(w_m\), update
   \[
   z\leftarrow \bigl(z+|w_m|V(w_m)+\pi_m\bigr)\bmod|W|,
   \]
   with \(m\) starting at 1 and \(j\) never resetting. Apply the shared codec; skipped F’s contribute to the completed plaintext word’s gematria but consume no immediate key symbol.

   **(b) Key material.** The four plain pages and GP arithmetic. Clear word boundaries provide the update clock.

   **(c) Cheapest falsifying test.** Decode the first 60 complete words of each section. **Reject if pooled unigram LLR is \(\le0\)** under passing same-length controls. This is particularly cheap because a wrong first-word result usually sends every subsequent address down the wrong route.

   **(d) Ledger proximity.** E0009, E0015, and E0007. New: the next word’s route depends on the previous word’s recovered content; there is no shared “position within word” key and no reset to a common word-start state.

6. **The page-15 square as a signed steering wheel.**

   **(a) Rule.** Read the supplied 4×4 square row-major and set \(D_k=A_k-3301\). Starting at \(z=a_h\bmod|W|\), before each consumed rune update
   \[
   z\leftarrow(z+D_{j\bmod16}+\pi_{j+1})\bmod|W|,
   \]
   then use
   \[
   x_j=V(W_z)+29|D_{(j+1)\bmod16}|.
   \]
   The shared codec makes doublets rare-symbol escapes; F-skips suspend both the steering and prime clocks.

   **(b) Key material.** Exactly the printed 16 integers, 3301, primes, and the four-page word book. **Important arithmetic correction:** the supplied claim that every cell is \(3301\pm\) a prime is false as written: \(4516-3301=1215\) and \(3301-1206=2095\), both composite. This construction uses the literal integers and does not assume that claim.

   **(c) Cheapest falsifying test.** Apply the 300-rune LLR screen: **reject at LLR \(\le0\)** with passing controls. Any stricter proposal requiring all 16 differences to be prime is **already refuted by the supplied numbers**, before ciphertext analysis.

   **(d) Ledger proximity.** E0005/E0006/E0017 and B10. New: signed square entries steer an external book walk; they are not themselves reduced to a prime/Fibonacci keystream.

7. **The numbered list as a five-word stencil.**

   **(a) Rule.** For consumed position \(j\), choose
   \[
   z_j=(1033j+j^2+3301a_h)\bmod|W|,
   \qquad
   x_j=\sum_{r=1}^{5}r\,V(W_{(z_j+r-1)\bmod|W|}).
   \]
   Use the shared codec and F-skip rule. A doublet means that the five-word weighted sum selected the plaintext rune at the omitted alphabet position.

   **(b) Key material.** The literal **1–5 list**, cuneiform **1033 and 3301** in p33–39, and the four plain pages. This is an explicit interpretation of those numerals as addresses and weights rather than as a short numeric password.

   **(c) Cheapest falsifying test.** Generate 300 decoded runes per section. **Reject at pooled LLR \(\le0\)** with successful controls. Additionally, simulated ciphertext must pass the observed nonzero-step uniformity: **construction-versus-data Monte Carlo \(p<0.001\)** rejects its statistical fit even if a short language score looks promising.

   **(d) Ledger proximity.** E0022 and E0026. New: the numbers define a moving local stencil over book words rather than digits of a pad or a global one-number/one-word lookup.

8. **The 256-byte grid as instructions, not pad bytes.**

   **(a) Rule.** Read the decoded grid row-major as \(g_0,\dots,g_{255}\), and start \(z=a_h\bmod|W|\). Before each consumed rune set
   \[
   z\leftarrow(z+1+g_{j\bmod256}+j)\bmod|W|,
   \]
   and output
   \[
   x_j=V(W_z)+29g_{(z+a_h)\bmod256}.
   \]
   Apply the shared codec: doublets expose rare-symbol escapes, and F-skips pause the instruction pointer and book walk.

   **(b) Key material.** Exactly the supplied interpretation of the 8×32 grid and the four-page word book. Neither a byte reversal nor an offset search is part of this candidate.

   **(c) Cheapest falsifying test.** Decode the first 300 runes per section—enough to cross the grid’s 256-entry wrap. **Reject at pooled LLR \(\le0\)** with passing controls. Inspect the transition across consumed positions 255/256 explicitly; a candidate that only works before that wrap is not a fit.

   **(d) Ledger proximity.** E0023/E0026. New: grid bytes control cumulative movement and a second indexed read; they are neither a repeating pad nor independent global word addresses. This is a narrow, testable extension, not evidence that the grid must be a key.

9. **The missing-prime list as a ciphertext-steered route.**

   **(a) Rule.** Let \(M\) be the ordered list of all primes from 73 through 1223, inclusive; initialize \(r=0\), \(z=a_h\bmod|W|\). At each non-skipped position, using the preceding ciphertext rune \(c\), perform
   \[
   r\leftarrow(r+1+c)\bmod|M|,\qquad
   z\leftarrow(z+M_r+j)\bmod|W|,
   \]
   then take
   \[
   x_j=V(W_z)+29M_r.
   \]
   Apply the shared codec. F-skips change the preceding ciphertext to 0 but leave \(r,z,j\) unchanged.

   **(b) Key material.** Precisely the missing interval **73…1223** from the 2013 telnet prime list, the GP book, and section page numbers.

   **(c) Cheapest falsifying test.** Sequential decoding requires no plaintext-feedback search beyond the F branches. **Reject at pooled 300-rune LLR \(\le0\)** with passing controls. The complete missing interval—not a hand-selected subset—must be used.

   **(d) Ledger proximity.** E0007 and E0005/E0006/E0017. New: ciphertext steers a persistent two-address state through a book. It is not an additive lagged-ciphertext autokey or a raw prime-gap sequence.

10. **A hand-operated, self-mutating 28-card alphabet.**

   **(a) Rule.** Make a deck containing 0–27: put the distinct rune indices of **DIVINITY** first, in occurrence order—\(23,10,1,9,16,26\)—then append unused indices in increasing order; rotate left by \(a_h\bmod28\). Before each consumed rune use \(q_j=R[D_0\bmod4]\) and \(t_j=D_1\) in the shared rare-symbol codec, then rotate left by \(1+G(p_j)\bmod28\) and swap deck positions 0 and \((c_i+j)\bmod28\). F-skips do neither deck operation.

   **(b) Key material.** The already evidenced keyword **DIVINITY**, GP prime values, and section-start numbers. This is executable with 28 numbered slips and the printed prime table.

   **(c) Cheapest falsifying test.** Decode 300 runes per section and apply the **LLR \(\le0\)** rejection screen with exact-rule controls. Also record full deck states: **an identical full state at identical counter residue modulo 28** proves a repeat in the state trajectory, though translating that into a statistical contradiction still requires checking its subsequent inputs.

   **(d) Ledger proximity.** E0003 and E0007. New: a large evolving permutation driven by recovered plaintext and ciphertext, rather than a short repeating key or fixed-lag additive feedback. Doublets are active state-changing events because their decoded rare rune rotates the deck.

11. **Long division of the 2012 factors as a nonzero-step selector.**

   **(a) Rule.** Let \(P\) and \(Q\) be respectively the first and second supplied prime factors; initialize remainder \(r=(Q+a_h)\bmod P\). Repeatedly compute
   \[
   d=\lfloor1000r/P\rfloor,\qquad r\leftarrow1000r\bmod P;
   \]
   discard \(d\ge896\), and for each accepted block use \(x_j=d\bmod112\). The shared codec turns this into 28 shifts and four possible escape runes; F-skips consume no accepted block.

   **(b) Key material.** Exactly the two printed 2012 P.S. factors. The rejection boundary is \(896=8\times112\), avoiding the elementary bias from reducing 1,000 equiprobable blocks directly modulo 112.

   **(c) Cheapest falsifying test.** Generate only enough accepted blocks for the 300-rune screens. **Reject at pooled LLR \(\le0\)** with successful controls. Separately test accepted residues modulo 112 against uniformity; **\(p<0.001\)** rejects the proposed *flat-selector* justification, though not the mathematical existence of the long-division cipher.

   **(d) Ledger proximity.** E0022. New: digits of a rational expansion, rejection sampling, and an explicit 29-symbol codec—not the factors written in base 29. It is hand-checkable by long division, but considerably less economical than the book-walk candidates. Uniform-looking digits are a hypothesis, not a theorem here.

12. **A section-bound hash-and-grid pad with meaningful zero escapes.**

   **(a) Rule.** Decode the page-56 hexadecimal string to 64 bytes \(H\), and let \(G\) be the 256 grid bytes. For counters \(n=0,1,\dots\), concatenate
   \[
   \operatorname{SHA512}\!\left(
   \texttt{LP}\,\|\,H\,\|\,G\,\|\,\operatorname{uint8}(a_h)\,\|\,
   \operatorname{uint64be}(n)
   \right);
   \]
   discard output bytes \(\ge224\), and use each accepted byte modulo 112 as \(x_j\). Apply the shared codec and F rule, so doublets encode selected rare plaintext runes rather than arbitrary pad accidents.

   **(b) Key material.** Exactly the supplied page-56 hash bytes, row-major grid bytes, and section-start page numbers. `LP` means the two ASCII bytes `4c 50`; SHA-512 is a registered design choice here, not a claim about the unknown algorithm behind the printed hash.

   **(c) Cheapest falsifying test.** Decode 300 runes per section. **Reject at pooled LLR \(\le0\)** with successful controls; there are no seed, digest, byte-order, or offset alternatives in this candidate. Even a language-score pass must survive full-length round-trip checking and independent simulation of the doublet count: a pseudorandom selector gives expected escape frequency approximately
   \[
   \frac{f_J+f_{EO}+f_X+f_{OE}}4,
   \]
   not automatically \(86/12947\). A **doublet-count predictive \(p<0.001\)** rejects that fit.

   **(d) Ledger proximity.** E0021, with E0023 key material. New: a precisely specified composite, section-bound seed and rare-symbol differential codec. This is the least hand-executable and least stylistically economical candidate; its main value is as a sharply bounded computational alternative. None of these constructions earns the claimed fingerprint merely by being aperiodic or cryptographic—the count of 86 remains a substantive, independently testable prediction.
