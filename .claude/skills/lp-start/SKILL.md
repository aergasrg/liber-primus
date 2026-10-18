---
name: lp-start
description: Start a Liber Primus lab session cold - read the rules and state, pick and claim one backlog item, pass the gate, and write a short plan. Use at the beginning of every session in this repo.
---

# lp-start

1. **Read, don't skim** (in this order; do not print whole files to chat):
   - `CLAUDE.md` (rules), `docs/STATE.md` (facts), `docs/LEDGER.md` and `docs/BACKLOG.md` (generated).
   - The two newest notes in `docs/sessions/` (what was just done, what not to repeat).
   - If `docs/LEDGER.md` looks stale versus `docs/ledger/`, run `python3 scripts/build_index.py`.
2. **Sync**: `git fetch origin main` and merge `origin/main` into your branch so you see items claimed
   or finished by parallel sessions.
3. **Pick one item**: the one named in the prompt, else the lowest-rank item with `status: open`.
   Never take an item another branch has claimed unless its handoff note says it was abandoned.
4. **Claim it** in that item's own file only: set `status: claimed` and `claimed_by: <your branch>`.
   Run `python3 scripts/build_index.py`, commit (`Claim Bxx`) and push early so others see the claim.
5. **Environment**: `pip install -q numpy pyyaml pytest` if needed, `bash scripts/fetch_data.sh`, then the
   gate `python3 -m pytest -q tests/`. Stop and fix if it fails; nothing else is meaningful until it passes.
6. **Ledger check**: read every ledger entry linked from the item and every entry of the same family.
   Write down, in one or two sentences, exactly what is new about your variant.
7. **Plan** (a few lines, in the session, not a file): hypothesis, coverage, positive control, null,
   expected runtime, checkpoint plan. Then follow the lp-experiment skill.
