---
id: B02
title: Plaintext-reactive key rules over long key sources
status: open
claimed_by: ""
rank: 2
ledger: [E0006, E0007]
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
