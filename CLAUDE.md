# Liber Primus lab: rules for every session

## Hard rules (verbatim, non-negotiable)

- Python 3. Variables are PascalCase (RuneValues, KeyStream). Never SCREAMING_SNAKE for anything.
- No experiment is "negative" without (a) a positive control: a key planted in known plaintext and
  recovered through the identical pipeline, and (b) a null or noise ceiling. Record both.
- Check the ledger before running anything. Do not repeat an excluded family unless the variant is
  new, and say exactly what is new.
- Token frugality: never print whole data files or long outputs; print summaries; write results
  to files. Long jobs run in the background, log progress to a file and checkpoint, because idle
  cloud VMs pause and can be reclaimed.
- Never paste copyrighted text into the repo or chat. Public-domain texts are fetched by script
  into data/texts/. Do not copy code from github.com/Leo-Y-Zhang/LiberPrimusAnalysis (its licence
  is proprietary source-available): cite it, reimplement.
- Never print or commit API keys. OpenAI calls only through tools/ask_other_model.py (below).
- OpenAI models newer than your training exist. Read docs/models/openai.md before calling tools/ask_other_model.py.
- Never change the OpenAI service tier: every request sends "service_tier": "default" (Standard), never
  Fast, Ultrafast, priority or flex. A response reporting another tier writes budget/openai/STOP and
  the tool refuses all calls until a human deletes it; never delete it yourself. Never enable hosted
  tools (code interpreter, web search, file search, shell): calls are text only.
- One backlog item per session. Finish with the handoff skill.

## Orientation (read this, then docs/STATE.md)

1. Goal: an honest, reproducible lab notebook on the 9 unsolved Liber Primus sections (12,956 runes).
2. The one fingerprint: 86 doublets where ~446 are expected; everything else is flat (IoC ~1.00).
3. Working model: chain cipher c_i = c_(i-1) + s_i, s_i in 1..28, from a flat aperiodic key. Find the key source.
4. Every solved key came from LP's own plain pages, and every keyed solved page uses F-skips.
5. Setup: `pip install numpy pyyaml pytest`, then `bash scripts/fetch_data.sh` (data/ is gitignored).
6. Gate: `python3 -m pytest -q tests/` must pass before any experiment.
7. Library: `lp/` (gematria, data, stats, ciphers, detectors, controls, keysources). Import, don't copy.
8. Experiments: `experiments/E####_slug.py`; outputs to `results/E####/` (small text files only).
9. Ledger: one file per experiment in `docs/ledger/E####-slug.yaml`, append-only, never edit others'.
10. Backlog: `docs/backlog/B##-slug.md`; claim by setting `status: claimed` and `claimed_by: <branch>`.
11. Indexes `docs/LEDGER.md` and `docs/BACKLOG.md` are generated: `python3 scripts/build_index.py`.
12. New ledger id: `git fetch origin main`, take the next free E number; build_index flags duplicates.
13. Anything above its noise ceiling goes to the skeptic agent (.claude/agents/skeptic.md) first.
14. Handoff notes live in `docs/sessions/YYYY-MM-DD-<branch>.md`; read the latest two at start.
15. Seed code from session one is in `seed/seed_scripts/` (historical; ported into `lp/`).

## Pointers

- docs/STATE.md (facts), docs/HISTORY.md (2012-2017 trail), docs/LEADS.md (unused clues, exact values)
- Skills: lp-start, lp-experiment, lp-handoff, lp-budget, lp-data, lp-council (in .claude/skills/)
- Agents (.claude/agents/): skeptic; council (one OpenAI call per brief); worker (only inside this session's own item)
- OpenAI: tools/ask_other_model.py (budgeted, background calls); models and effort policy in docs/models/openai.md
- Network: a download blocked by the allowlist goes in docs/NETWORK.md for the human; don't work around it.
