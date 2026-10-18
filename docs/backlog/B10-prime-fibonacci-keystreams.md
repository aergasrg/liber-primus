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
