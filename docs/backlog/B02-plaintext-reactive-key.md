---
id: B02
title: Plaintext-reactive key rules over long key sources
status: open
claimed_by: ""
rank: 2
ledger: [E0006, E0007, E0028]
---

# B02 Plaintext-reactive key rules over long key sources

## Why
A key pointer that moves according to the plaintext (e.g. by the previous rune's prime) would flatten statistics and defeat fixed-offset scans, yet stay in the 'book's own numbers' spirit.

## Test design
1. Enumerate a small grammar of rules: pointer advance = prime(prev plain), index(prev plain), prev cipher;
   skip when output would repeat (would explain doublet suppression!), etc.
2. Key sources: LP solved plaintext, the long texts from B03, sequences.
3. Hill-climb or beam search with an n-gram model; plant each rule in solved plaintext as the control.
4. Null: same search on shuffled ciphertext; report the best-score ceiling.

## Notes
Design-heavy: suits Fable 5.1. The doublet rate 0.66% vs 3.45% is the target the rule must reproduce.

## Target from B12 (E0028)
A candidate rule must reproduce, on solved plaintext through its own pipeline:
- **Leak rate**: repeats avoided except for a leak at about 1/5 of the random rate (86 doublets where
  ~446 are expected, 0.19; per section 3-18, consistent with one rate everywhere).
- **Memoryless placement**: no clustering (gap CV 0.95, Fano 0.91), no packets, no period, no line/page
  start excess, no detectable rune preference. A leak that fires independently at each position fits;
  a leak tied to a regime of 20+ positions does not (stay >= 0.95 excluded).
- **Hard constraints**: the minimum gap is 6, so any strict refractory window must be <= 6 positions;
  one per printed line is impossible; one-per-P packets need P <= 14 (section-aligned) or <= 18
  (page-aligned).
- **Soft hint (not significant, p 0.12)**: no gaps <= 5 where ~2.6 are expected. A rule whose leak
  cannot recur within ~5 positions is favoured slightly over a pure Bernoulli leak.
- Example shapes to plant: "skip the key symbol that would give step 0, except when <condition with
  probability ~0.19 per position>", where the condition is independent of position, such as a key
  symbol in a set of 5-6 of 29, or a plaintext rune class holding ~19% of English text.

## Council midpoint addition (docs/council/2026-10-18/08-gpt-6-astra-midpoint-ideas.md, construction 6)
A rule shape to plant: the excluded symbol is normally c_(i-1), and the exclusion is released (a doublet
becomes possible, rate 1/28) when the plaintext rune five positions back lies in a class holding ~19%
of encoded text, e.g. {R, N, S} = {4, 9, 15}. Predicted q = f / 28 ~ 0.0068. Measure f on solved LP;
do not tune the class or the delay on the unsolved doublets. Ciphertext-only power is low, so this
belongs with a key search, not as a standalone placement test.
