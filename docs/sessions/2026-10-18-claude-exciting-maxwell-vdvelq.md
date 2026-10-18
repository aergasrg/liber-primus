# 2026-10-18 claude/exciting-maxwell-vdvelq

Item: maintenance, OpenAI helper v3 (no backlog item)  |  Status: done
Ledger: none (no experiments)

## What I did
- `docs/models/openai.md` (dated 2026-10-17, with source links). It covers gpt-6-astra (use),
  gpt-6.1-sol (fallback), gpt-6-luna and gpt-5.6-sol (skip), the ids that are live but unused, the
  pro mode, reasoning-token billing, the effort policy, the budget and the refresh rule. CLAUDE.md
  now points to it.
- `tools/ask_other_model.py` v3, standard library only:
  - `--list-models` (flags recent text ids the doc doesn't describe).
  - Background Responses calls, polled every 15 s, cancelled at the deadline.
  - The fixed developer message.
  - Pro fallback to standard mode, once.
  - Flagged and incomplete handling.
  - A budget ledger under an fcntl lock with reservations, merged by id with origin/main.
  - The refresh rule, enforced: it refuses undescribed models and a doc over 30 days old.
  - Saves every call to `docs/council/<date>/`.
  The ledger uses git's union merge driver (`.gitattributes`).
- `tests/test_ask_other_model.py` (10 tests) runs against a local mock server. It covers completed,
  incomplete, failed, flagged with no retry, a pro call that never finishes and falls back, reserve
  and cap refusals, two parallel calls, dry run and policy refusals, and the ledger merge.
- Agents: council (sonnet, one call per brief), worker (sonnet, only inside the session's own item),
  skeptic set to fable. Skill: lp-council with its four phases. lp-budget was updated.
  `docs/NETWORK.md` is new.
- seed/PROMPTS.md: the worker line now says a wave is 2-3 separate sessions with one item each.

## Results
- Live: `--list-models` returned 139 ids, none undescribed. One smoke call (gpt-6-luna, effort none,
  max-output 200) completed and used 50 tokens. Budget left: 169,950 general, 219,950 including the
  reserve.
- Gate: 17 tests pass (7 gate tests and 10 helper tests).

## Next steps (most useful first)
- Merge this PR, then run `Run the lp-council skill, kickoff phase.` in exactly one session.
- B01 skip-tolerant running-key engine (as before).

## Do not repeat
- Don't spend tokens re-testing the helper live. The mock tests cover it.

## Needs a human
- Nothing. The proxy injects the API credential, and no OPENAI_API_KEY is needed.
