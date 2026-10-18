---
id: B20
title: PRNG seeds from release timestamps (32-bit range)
status: open
claimed_by: ""
rank: 18
ledger: [E0019, E0020]
---

# B20 PRNG seeds from release timestamps (32-bit range)

## Why
E0019/E0020 swept seeds 0..2^20 (Perl, glibc) and 0..2^18 (Python): 1/4096 and 1/16384 of a 32-bit
seed space. A program seeded from the clock (time() or a date) at the 2014 release sits far outside
those ranges. Council audit T3 gap 3 (docs/council/2026-10-18/04-gpt-6-astra-kickoff-negatives.md).

## Test design
1. Freeze a registry of authenticated timestamps before scanning: the 2014 onion publication times
   of the Liber Primus pages, the signed-message dates (2012-01-04, 2013-01-04, 2014-01-05, 2016, 2017),
   and the dates printed or implied in the pages. Record the registry in the ledger entry.
2. For each timestamp, every integer second within +-7 days (1,209,601 seeds per interval), through
   each generator's real seed conversion (drand48's 48-bit state from a 32-bit srand argument, glibc's
   32-bit srand, Python's arbitrary-width int).
3. Scan with the B19 engine (page starts, skip-aware, both zero conventions, the wrappers).
4. Control: plant a seed from inside a high-valued interval, not a low integer. Null: as B19.

## Notes
Cost per interval and generator about 6.3e10 symbol visits before skip states; one interval is a
background job of hours, so run the registry in order of plausibility and checkpoint. A full 32-bit
sweep (2.2e14 per generator) is out of budget and would still not cover Python string seeds.
