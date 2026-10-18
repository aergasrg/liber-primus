---
id: B10
title: Prime-Fibonacci keystreams
status: open
claimed_by: ""
rank: 10
ledger: []
---

# B10 Prime-Fibonacci keystreams

## Why
The page-15 square is 3301 +- primes whose prime indices are Fibonacci numbers (Zeckendorf spiral). The same construction could generate a keystream.

## Test design
1. Build keystreams: primes at Fibonacci indices, their differences from 3301, the square read as a spiral,
   Zeckendorf digits; mod 29 and in chain form.
2. Scan raw and chain at section starts and every offset; include F-skip variants.
3. Control: plant the stream; null: random prime-index sets of the same size.

## Notes
Square: 3258 3222 3152 3038 / 3278 3299 3298 2838 / 3288 3294 3296 2472 / 4516 1206 708 1820.
Exact rule verified 2026-10-18 (see docs/LEADS.md): cell = |3301 - B| with B the primes at 0-based
Fibonacci indices, B = 2, 3, 5, 7, 13, 23, 43, 79, 149, 263, 463, 829, 1481, 2593, 4507, 7817, in a
spiral. So the natural keystreams are B itself (and its continuation: primes at index F_n for larger
Fibonacci numbers), |3301 - B|, and the spiral order of the cells; the Zeckendorf digits of n are a
separate stream. Council note: 149 (B_9) equals the fitted 1/P(step 0) = 12947/86; probably chance.
