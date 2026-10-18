# 2026-10-18 claude/nifty-ride-hy6cds

Item: OpenAI tool changes (service-tier lock, rolling 24 h budget) + council midpoint phase (no backlog item)  |  Status: done
Ledger: none (the council runs no experiments)

## What I did
- **Service-tier lock** (`tools/ask_other_model.py`). Every request sends `"service_tier": "default"`.
  - A live gpt-6-luna call (effort none, max-output 200, council file 05) reported `default` on both the
    create and the completed response, so that value is pinned (`ServiceTier`).
  - Any response that reports another tier is cancelled, logged `tier-violation` (exit 4), and writes
    `budget/openai/STOP`. A final response that reports no tier is treated the same way.
  - While STOP exists locally or on origin/main, the tool refuses everything, `--list-models` included.
  - The request body is whitelisted (`AllowedBodyKeys`): no `tools`, so text only.
  - Final ledger entries now record `service_tier`.
  - The rule is in CLAUDE.md, lp-budget, lp-council, the council agent and docs/models/openai.md.
- **Budget** is now a rolling 24 h window: Cap = min(OPENAI_TOKEN_CAP or 230000, 230000) - 10000, summed
  over the ledger entries of the last 24 h.
  - The 50k reserve and `--use-reserve` are gone. Verify calls go first on any day.
  - Pro mode: at most once per 24 h, only with 60k+ left in the window; the tool enforces both.
  - Ledger history is unchanged.
- **Tests**: 25 pass. New tests cover:
  - the rolling window and entries rolling off;
  - the pro rule;
  - three tier-violation paths (on create, mid-poll, missing on the final response), each writing STOP;
  - STOP blocking all calls until deleted;
  - every request body pinning the default tier.
- **Council midpoint**: two high bug hunts (lp/runningkey.py; the E0030 column-LLR scorer) and one xhigh
  idea round on the B12 target. Details are in docs/council/2026-10-18/README.md (midpoint section).

## Results (control / null / best)
- Bug hunt: **one confirmed coverage bug**. In lp.runningkey's step views, an F inside an FF run can never
  skip.
  - Real impact: 4 FF pairs, on pages 9, 29, 32 and 36, in the step views only.
  - Plant defects in both engines only make plants harder, so the recorded power is conservative.
  - No verdict changes for E0027 or E0030, nor for E0029 outside those four pages. All of it is in B24.
- Ideas: 8 constructions, all built on one "excluded-symbol" core. Five control laws have key-free tests
  that take seconds (B25). The council ranks the stale-exclusion register first: it predicts lag-4
  coincidences of about 357 where 446 are expected.
- OpenAI spend: phase 61,949 tokens. The window had 106,176 left at about 23:05 UTC; the kickoff's 51,825
  rolls off at about 17:44 UTC on 2026-10-19.

## Next steps (most useful first)
- B25 (rank 2): five preregistered key-free statistics. Cheapest high-power check of the B12 target.
- B24 (rank 3): fix the step-view F-runs in lp.runningkey and in gpu/E0029_bytes_gpu.py *before* the GPU
  job runs, then rerun the step views on the 4 FF pages.
- Merge this PR before the next council phase (one key-using session at a time).

## Do not repeat
- The midpoint bug hunts and the idea round (replies saved as council files 06-08).
- The service-tier smoke test; the tier is pinned.
- Construction 1 (Bernoulli puncture leak): untestable by placement.

## Needs a human
- If `budget/openai/STOP` ever appears, read it, fix the cause, and delete it by hand; no session may.
- Earlier decision still open: whether the audit's null rule goes into lp-experiment.
