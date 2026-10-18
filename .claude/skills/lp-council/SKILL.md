---
name: lp-council
description: Run one OpenAI council phase for the Liber Primus lab (kickoff, midpoint, final, or verify on a ledger id) - a short brief, a few budgeted calls to gpt-6-astra through tools/ask_other_model.py, dedupe against the ledger, file backlog items, then a README and lp-handoff. Use only when the prompt names a phase.
---

# lp-council

The council gives second opinions. It never runs experiments; workers test what it suggests.
The token budget is 220k per rolling 24 hours (see `docs/models/openai.md`), so every call counts.
Never change the service tier (`default`, pinned) and never enable hosted tools. If
`budget/openai/STOP` exists, stop: only a human may delete it.

## Every phase starts here

1. **One key-using session at a time.** Run `git fetch origin main`, then check two things.
   First, `git show origin/main:budget/openai/ledger.jsonl | tail -5`: a `reserved` entry with no
   final entry, from another session in the last hour, means a call is still running. Second, open
   PRs or branches that touch `docs/council/`. If either shows another session using the key, stop
   and tell the human. Merge each council PR before the next phase.
2. `python3 tools/ask_other_model.py --list-models`. Apply the refresh rule: if
   `docs/models/openai.md` is over 30 days old, or the tool lists an id the file doesn't describe,
   look the model up (web search, developers.openai.com/api/docs/models), update the file and bump
   `updated:`. Do this before any call.
3. Read `docs/models/openai.md` (models, effort policy, budget) and the lp-budget skill.
4. Briefs go in `docs/council/<date>/brief*.md`. They use rune numbers (0-28 in gematria order) or
   Latin letters, never rune characters. Each stays under 5,000 tokens (about 15,000 characters) and
   holds no copyrighted text. Check the size: `wc -c`.
5. Make each call with the council agent (`.claude/agents/council.md`), one call per agent, or
   run the tool directly. Always `--dry-run` first. Model: gpt-6-astra. Switch to gpt-6.1-sol only
   if Astra flags the request or the key can't reach Astra.

## Phases

### kickoff (about 75k)

1. Write `brief.md`: the fingerprint (12,956 runes, 86 doublets where about 446 are expected, IoC
   about 1.00, a flat step histogram), the working model (chain c_i = c_(i-1) + s_i, s_i in 1..28),
   how each solved page was solved (keys from LP's own plain pages, F-skips), the leads in
   `docs/LEADS.md` with exact values, and the 15 biggest negative families from `docs/LEDGER.md`
   with one line each on what was covered.
2. Two calls at **medium** (max-output 16000), both asking: "Give 12 concrete, testable
   constructions that would produce exactly this fingerprint, each with its cheapest falsifying
   test." Frame one as a cryptanalyst (`--purpose kickoff-cryptanalyst`) and the other as a
   puzzle designer working in Cicada's style (`--purpose kickoff-designer`).
3. Dedupe the 24 ideas against `docs/ledger/` (by family and coverage). File the best untried ones
   as `docs/backlog/B##-slug.md` (next free numbers, `status: open`). Each needs a test design with
   a positive control and a null. Cite the council file it came from.
4. One call at **high** (max-output 25000, `--purpose kickoff-negatives`): "How could our 3 most
   important negative tests have missed a real signal?" Name the three ledger entries and give their
   coverage, control and null. File each concrete gap it finds as a backlog item, or as a rerun item
   if the gap is real.

### midpoint (about 65k, after the first wave of worker results is merged)

1. **Bug hunt** at **high** (`--purpose midpoint-bughunt`). Send the newest engine code: the `lp/`
   modules and experiment scripts added since kickoff, trimmed to the relevant functions and kept
   under the 5k-token brief limit. Send the ledger entries that rely on that code with them. Ask for
   concrete bugs: alignment, off-by-one, sign, F-skip handling, null construction, leakage. Each
   bug comes with a failing input. Fix confirmed bugs, or file them as backlog items, and rerun the
   affected controls.
2. **Fresh ideas** at **medium** (`--purpose midpoint-ideas`). Start from what failed and why (the
   new ledger entries, their best scores against their ceilings). Ask for constructions that would
   explain those failures. Dedupe and file the ideas as in kickoff step 3.

### final (about 30k plus whatever the 24 h window has left, in the project's last week)

1. **Whole-ledger review** at **high** (`--purpose final-review`). Send a compact table of every
   ledger entry: family, coverage, control score, null ceiling, verdict. Ask which negatives are
   weakest, what is still untried, and what one experiment the remaining credits should buy.
2. **The pro question**, only if 60k or more remains in the 24 h window after step 1 (check with
   `--dry-run`). Use `--mode pro --effort high --max-output 40000 --purpose final-pro` on the single
   hardest open question. At most once per 24 hours; the tool refuses a second pro call in the
   window and a pro call with under 60k left. If the pro call times out or fails, the tool falls back once
   to standard mode by itself. Do not retry beyond that.

### verify (on a ledger id; goes first on any day)

Use this phase any time a result beats its noise ceiling and the skeptic agent has already reviewed
it (`results/<id>/skeptic.md`).

1. Brief: the method, the evidence (scores and positions, never rune characters), the positive
   control, the null and its trial count, and the skeptic's report.
2. One call at **high** with `--purpose verify` (there is no reserve; make it before other calls that
   day so the window has room): "Attack this claim
   independently: find the artefact, the leak or the multiple-testing error that explains it, and
   the one test that would settle it." Record the verdict next to the skeptic's verdict in the
   ledger entry's follow-up (a new ledger file if that entry belongs to another session).

## Every phase ends here

1. `docs/council/<date>/README.md` with the phase, each call (saved file, model, effort, status,
   tokens), the remaining budget, the backlog items filed (ids), and the ideas dropped as duplicates
   (with the ledger ids they duplicate).
2. Commit `budget/openai/ledger.jsonl` and `docs/council/<date>/`. Never commit keys.
3. Run the lp-handoff skill.
