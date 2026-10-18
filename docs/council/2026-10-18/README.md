# Council, 2026-10-18: kickoff phase

Session branch: claude/stoic-feynman-g6muzj. Model gpt-6-astra throughout; no call was flagged.
Briefs: `brief.md` (shared evidence body, 9,636 chars), `brief-cryptanalyst.md`, `brief-designer.md`,
`brief-negatives.md` (14,325 chars). All in rune numbers or Latin letters.

## Calls

| file | purpose | effort / max-output | status | tokens (in / out incl. reasoning / total) |
| --- | --- | --- | --- | --- |
| 01-gpt-6-luna-smoke.md | smoke (previous session) | none / 200 | completed | 45 / 5 / 50 |
| 02-gpt-6-astra-kickoff-cryptanalyst.md | kickoff-cryptanalyst | medium / 16000 | completed | 3,491 / 9,800 (6,214 reasoning) / 13,291 |
| 03-gpt-6-astra-kickoff-designer.md | kickoff-designer | medium / 16000 | completed | 3,560 / 10,793 (6,178 reasoning) / 14,353 |
| 04-gpt-6-astra-kickoff-negatives.md | kickoff-negatives | high / 25000 | completed | 4,508 / 19,673 (12,948 reasoning) / 24,181 |

Phase total 51,825 tokens (plan was about 75k). Spent on the project: 51,875.
**Remaining: 118,125 general, 168,125 including the 50k reserve** (cap 220,000).

## Backlog items filed

From the two kickoff calls (02, 03):
- B12 structure of the doublet event process: seed-free spacing, autocovariance, within-word clustering
  and packet-occupancy tests (02 items 3, 4, 8, 9, 10). Cheap; discriminates mechanism classes.
- B13 doublets as escapes for a set of rare plaintext runes (03 shared codec). Measured here: the five
  rarest runes total 0.34% (baseline 0.37%), six 0.87% (0.80%), observed 0.664%; no set fits exactly.
- B14 self-addressing walks through LP's own plain pages with exact update rules (03 items 2, 4-9).
- B15 deck and permutation-state keystreams, Solitaire-style (03 item 10).
- B16 expansion digits of Cicada numbers as keystreams, Q/P, 1/P, sqrt(3301) etc. (03 item 11).
- B17 hash pads from binary leads with section labels, a bounded extension of E0021 (02 items 1, 2, 6, 7;
  03 item 12).

From the negatives audit (04):
- B18 rerun E0002 in the step domain, page by page, with bounded F-skips (T1 gaps 1-3). Rank 3.
- B19 rerun E0019/E0020 page-locally, skip-aware, with reduction wrappers (T3 gaps 1, 2, 4). Rank 4.
- B20 PRNG seeds from release timestamps (T3 gap 3).
- B01 (open, unclaimed) gained a "Council additions" section with the four T2 gaps: page-local
  alignment with 0-11 skips per page, raw/step/chain representations, a digraph tokenisation lattice,
  and the eight direction/polarity forms, plus the plants and the null the engine must pass.

Methodological rule from 04, adopted in B18, B19 and B01: the null is the whole optimised search run on
999 surrogate corpora (non-zero steps permuted within pages, zero positions and boundaries kept,
re-integrated from random page-initial runes, F positions recomputed); a hit is max-search p <= 0.01,
confirmed by a continuation under the frozen key. Plants must carry the feature the gap is about and
be recovered in >= 95 of 100. A fixed 1.25 IoC cutoff is not valid after widening a search.

## Ideas dropped as duplicates or untestable

- 02 items 1, 2, 5, 6, 7, 11, 12 (hash-expanded gates and constrained-output codecs seeded from the
  leads, with P(step 0) = 1/149 fitted to 86): same family as E0021 (hash pads) and E0013; untestable
  without the seed, and 02 itself says their observable distributions coincide. Their seed-free
  predictions are B12; the new seeds are B17.
- 03 item 3 (page-line-word prime book code over the four plain pages): duplicate of B11.
- 03 item 1 (prime-addressed book plus rare-symbol codec): split into B13 (codec) and B14 (walk).
- 03 item 4 (plaintext-driven walk): overlaps B02; kept inside B14 as the shared-control rule.
- 03 item 12 (SHA-512 of hash || grid || page number || counter): E0021 family; folded into B17.
- 04's "not worth rerunning" lists are copied into B18, B19 and B01 so nobody spends on them.

## Corrections found while deduping

- 03 item 6 claimed the page-15 square is not 3301 +- primes (4516 and 1206). Wrong: the exact rule is
  cell = |3301 - B| with B the primes at 0-based Fibonacci indices (mortlach, 2016); 4516 and 1206 come
  from 7817 and 4507. docs/LEADS.md and B10 now state the rule exactly.
- The rare-rune frequencies above were computed from the solved pages (2,979 runes) and the baseline
  corpus (2.37M runes) with `lp.data`; they are facts for B13, not an experiment.

## Next phase

Midpoint, after the first wave (B01 with the council additions, B18, B19, B12) is merged. Budget
left for it: 65k planned, 118k available.

---

# Council, 2026-10-18: midpoint phase

Session branch: claude/nifty-ride-hy6cds. Model gpt-6-astra throughout; no call was flagged. Every
response reported `service_tier: "default"` (Standard), which the tool now pins (see
docs/models/openai.md). Briefs: `brief-midpoint-bughunt-runningkey.md` (14,938 chars),
`brief-midpoint-bughunt-columnllr.md` (10,274), `brief-midpoint-ideas.md` (6,244). All use rune numbers.

## Calls

| file | purpose | effort / max-output | status | tokens (in / out incl. reasoning / total) |
| --- | --- | --- | --- | --- |
| 05-gpt-6-luna-smoke-service-tier.md | service-tier smoke | none / 200 | completed | 44 / 5 / 49 |
| 06-gpt-6-astra-midpoint-bughunt-runningkey.md | midpoint-bughunt-runningkey | high / 25000 | completed | 4,472 / 12,506 (10,358) / 16,978 |
| 07-gpt-6-astra-midpoint-bughunt-columnllr.md | midpoint-bughunt-columnllr | high / 25000 | completed | 3,079 / 15,394 (12,948) / 18,473 |
| 08-gpt-6-astra-midpoint-ideas.md | midpoint-ideas | **xhigh** / 40000 | completed | 1,929 / 24,520 (20,194) / 26,449 |

Phase total 61,949 tokens (plan about 65k). The bug hunt was split into two calls, one per engine, to keep
each brief under 5k tokens. The ideas call ran at xhigh, not medium: the prompt made B12's target the
central question, and the effort policy gives xhigh to "the single hardest question of a phase".
**Budget is now a rolling 24 h window: 106,176 left at 23:0x UTC** (cap 220,000). The kickoff's 51,825
rolls off at about 17:44 UTC on 2026-10-19.

## Bug hunt: what was checked, and the outcome

lp/runningkey.py (E0029), 06:
- **Confirmed, B24 item 1**: in the step views only an isolated ciphertext F may skip. A skip inside an FF
  run, or beside a keyed F, cannot be scored. Reproduced with the council's input. On real data that is
  4 FF pairs, on pages 9, 29, 32 and 36, in the step views only; raw29 is unaffected. E0029's "any skip
  set" claim fails there, and a four-page step-view rerun is in B24.
- **Confirmed, minor (B24 items 2, 3)**: plant doublet multiplicity, and a doublet that resets the state
  after a transparent skip. Real layouts have 0 triples and 1 terminal doublet. The plant defects only
  make plants harder, so the recorded power is conservative.
- Harness and hardening (B24): plant offset ranges, the reversed-source label, a degenerate Gumbel scale,
  and the Weights normalisation (1e-5 per rune).
- **Not a bug**: the byte-null "shuffle after tiling" concern. E0029's BuildSource shuffles before tiling.

E0030 column-LLR scorer, 07:
- The mask cap (MaxK falls on pages with > 12 Fs) is already disclosed in the E0030 ledger: not new.
- `Var[1] = 0` exactly, and `Var[0] = 1` is fictitious. Checked: the real search's minimum mean column size
  is 3, so neither drives a score. Hardening is in B24.
- Plant defects (a doublet overrides a skip, a doublet resets state, early-biased capped skips): plants get
  harder, so power is conservative. In B24.
- z2 double-counting of an F-F zero step: the search still finds the plant with one skip fewer, so only
  the skip attribution is wrong. Recorded in B24 as a note.
- **No E0027/E0030 verdict changes.** No E0029 verdict changes outside the four FF pages.

## Ideas: backlog items filed

- **B25** (rank 2): key-free tests of five repeat-avoiding leak laws from 08, built on the council's
  common core (ciphertext drawn from the 28 runes other than an excluded h; usually h = c_(i-1)):
  - lag-k coincidences k 2..10 (construction 4, the stale exclusion register, predicts R_4 ~ 357 vs 446);
  - a preceding-step gate (2);
  - a running-checksum phase gate (3);
  - a step-band deficit (7);
  - the guard and word-lane rules (8, 5).
  One preregistered family, positive controls through the core, permutation and Markov nulls.
  Seconds of compute.
- **B24** (rank 3): the engine fixes above.
- **B02** gained construction 6, a leak gated by a plaintext class five runes back, as a rule shape to
  plant.

## Ideas dropped

- Construction 1 (a Bernoulli puncture leak): observationally identical to E0028's memoryless null, so
  untestable by placement.
- Arithmetic on the STATE.md step histogram, not a test: {1..5} holds 0.1778 of non-zero steps
  (z -0.22). Construction 7's five-hole band predicts z -1.75, and its one-hole variant predicts more.
  Both stay in B25 for the calibrated test.
- The council's AES-CTR key expansion is scaffolding for the core, not a seed to search. It stays out of
  E0019/E0020/B19 (PRNG families).
