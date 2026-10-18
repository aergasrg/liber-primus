---
id: B16
title: Expansion digits of Cicada numbers as keystreams
status: open
claimed_by: ""
rank: 16
ledger: [E0022]
---

# B16 Expansion digits of Cicada numbers as keystreams

## Why
E0022 used the Cicada numbers' own base-29 digits (a few hundred symbols at most). A rational or
irrational expansion is as long as needed, flat, aperiodic, and hand-computable by long division:
the 2012 P.S. factors P and Q give Q/P, 1/P, 1/Q; 3301 and 1033 give 1/3301, sqrt(3301), 3301^(1/3).
Council designer call, item 11 (docs/council/2026-10-18/03-gpt-6-astra-kickoff-designer.md), with
its rejection rule for an unbiased reduction.

## Test design
1. Streams: digits of Q/P, P/Q, 1/P, 1/Q, 1/3301, 1/1033, sqrt(3301), sqrt(1033), 3301^(1/3) in bases
   10, 29 and 28 (first 2,000 digits each); reduce base-10 blocks of three digits mod 29 / 28 with
   rejection above 986 / 980 (the council's unbiased rule); both digit orders.
2. Scan as E0022: each section start, both signs, raw and chain; plus every offset up to 1,000
   (FftRunningKeyScan).
3. Control: plant one stream over solved plaintext. Null: 200 random digit streams of the same
   length through the same scan; random 99th percentile per stream.

## Notes
Pi and e digits were done in E0017 (sequence family) and are not repeated.
