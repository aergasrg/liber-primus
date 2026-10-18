# Liber Primus lab: Claude Code cloud prompts

Prompts for new cloud sessions at claude.ai/code on the repo: the bootstrap that builds the repo,
the OpenAI helper v3 upgrade, a worker prompt for every later session, an open-ended hunt, the
OpenAI council phases, and a review prompt.

## One-time setup (5 minutes, before session 0)

1. Create an empty GitHub repo (for example `liber-primus-lab`) and install the Claude GitHub App on it.
2. Optional but recommended: unzip `lp-seed.zip` into a folder named `seed/` in the repo and commit it.
   The bootstrap session then ports working, verified code instead of rewriting it.
3. Cloud environment for this repo (claude.ai/code, edit environment):
   - **Network access: Full** if the OpenAI key goes in as an API credential (or you skip the
     key). Nothing secret is on the machine then, and sessions never stall on a blocked site. If
     the key has to be an environment variable, pick **Limited**, keep "Allow package managers"
     checked, and paste this into Allowed domains:
     ```
     api.openai.com
     developers.openai.com
     platform.openai.com
     gutenberg.org
     *.gutenberg.org
     wikisource.org
     *.wikisource.org
     sacred-texts.com
     *.sacred-texts.com
     *.fandom.com
     *.nocookie.net
     cicadasolvers.com
     *.cicadasolvers.com
     archive.org
     *.archive.org
     ```
   - **Environment variables** (anyone using the environment can read these, so no secrets here):
     ```
     BASH_DEFAULT_TIMEOUT_MS=600000
     BASH_MAX_TIMEOUT_MS=1800000
     OPENAI_TOKEN_CAP=230000
     ```
     The first two let Claude wait up to 10 minutes on a command (30 if it asks) before Claude Code
     moves it to the background. The cap is read by tools/ask_other_model.py, which stops at 220k
     and holds 50k of that back for checking results. There is no model variable: each call names
     its model. A running session keeps old values until its machine restarts, so start a new
     session after changing them.
   - **OpenAI key (optional):** on Pro or Max, edit the environment and use **API credentials** →
     Add credential: type Bearer, allowed website `api.openai.com`, header `Authorization`, prefix
     `Bearer`, paste the key, Connect. The key never enters the VM, and that host gets through the
     network allowlist automatically. Without that section, put `OPENAI_API_KEY=...` in the
     variables and use Limited (above). Give the key a lifetime that runs to the end of the
     project, not one day (see "OpenAI council phases"), and delete it when the project ends.
   - **Setup script:** `pip install numpy scipy sympy pyyaml`
4. Models: Opus 5.5 for the bootstrap and most workers. Save Fable 5.1 for design-heavy items
   (B02, B04) and the review session.

---

## Session 0: bootstrap (paste as the first message)

```text
You are setting up a long-running research repo for Cicada 3301's Liber Primus (LP). Many cloud
sessions (Opus 5.5 and Fable 5.1, often in parallel) will work in this repo over the next weeks.
Your job in THIS session: build the repo so any later session can start cold, know everything
already learned, never repeat a finished experiment, and hand off cleanly. We do not expect to
solve LP; we want a clean, honest, reproducible lab notebook with real new negatives or a lucky hit.

HARD RULES (put these in CLAUDE.md verbatim)
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
- One backlog item per session. Finish with the handoff skill.

REPO TO BUILD
- CLAUDE.md: rules above, a 15-line orientation, pointers to docs and skills.
- README.md: human overview, how to run the gate, how sessions work.
- docs/STATE.md: everything in FACTS below, compact and exact.
- docs/HISTORY.md: the 2012-2017 trail as one table (short).
- docs/LEADS.md: loose ends and unused clues (LEADS below), with exact values.
- docs/ledger/E####-slug.yaml: one file per experiment (append-only, so parallel sessions never
  conflict). Fields: id, title, family, hypothesis, coverage, detector, control {method, score},
  null {method, ceiling}, result {best, verdict: negative|positive|inconclusive}, skips_handled,
  source, date, artifacts. Seed it with every entry in PRIOR WORK and THIS RUN below.
- docs/backlog/B##-slug.md: one file per idea with a status header (open|claimed|done), claimed_by
  (branch), rank, why, test design, linked ledger ids. Seed from BACKLOG below.
- docs/sessions/YYYY-MM-DD-<branch>.md: handoff notes (template in the handoff skill).
- scripts/build_index.py: regenerates docs/LEDGER.md and docs/BACKLOG.md tables from those files.
  Sessions never hand-edit the generated tables.
- lp/ package: gematria.py, data.py (loader keeping word, sentence, line and page positions),
  stats.py (IoC, doublets, steps, chi2), ciphers.py (Vigenere, Beaufort, Atbash, shifts, totient
  stream, autokey, chain form, F-skip handling), detectors.py (IoC raw mod 29 and chain mod 28,
  English unigram log-likelihood, FFT running-key scan), controls.py (plant and recover),
  keysources.py (sequences, PRNGs: Perl drand48 and glibc rand bit-exact, hash pads).
  Port from seed/seed_scripts/ if present (verified code from session one).
- scripts/fetch_data.sh: downloads into data/ (gitignored): relikd's transcription
  raw.githubusercontent.com/relikd/LiberPrayground/main/pages/<name>.txt for p0-2, p3-7, p8-14,
  p15-22, p23-26, p27-32, p33-39, p40-53, p54-55, 0_warning, 0_welcome, 0_wisdom, 0_koan_1,
  0_loss_of_divinity, p56_an_end, p57_parable and the solved_*.txt files, plus
  data/baseline-rune-words.txt (English corpus in runes) from the same repo. Format: runes,
  "•" word break, "⁘" sentence end, "⁚" colon, "⁜" heading end, blank line = page break (unreliable,
  see pitfalls), digits and Latin letters are not runes.
- tests/test_gate.py: must pass before any experiment: reproduce Welcome (Vigenere DIVINITY with
  the 4,5,6,7,10,11,14,18,20,21,25th ciphertext F passing through without consuming key), Koan 1
  (Atbash then +3) and the unsolved stats (12,956 runes, 86 doublets).
- tools/ask_other_model.py: a stub that prints "not set up yet". A later "OpenAI helper v3"
  session builds it.
- .claude/skills/ (each a folder with SKILL.md and frontmatter name + description):
  lp-start (read CLAUDE.md, STATE, generated indexes; pick the top open item or the one named;
  claim it by setting status: claimed and claimed_by in that item's file; plan), lp-experiment
  (hypothesis, coverage, control, null, run, recheck top hits on full sections, record YAML),
  lp-handoff (ledger entries, item status, handoff note, build_index, commit, push, open a PR),
  lp-budget (frugality rules, the OpenAI wrapper, the cap), lp-data (loading, conventions,
  pitfalls below).
- .claude/agents/skeptic.md: a subagent that attacks a claimed result (re-runs the control,
  checks off-by-one alignment, multiple testing, leakage, and full-section recheck) and reports
  whether the claim survives.

FACTS (from the 17 Oct 2026 session; numbers verified from relikd's transcription)
- Gematria Primus, index rune latin prime: 0 ᚠ F 2, 1 ᚢ U/V 3, 2 ᚦ TH 5, 3 ᚩ O 7, 4 ᚱ R 11,
  5 ᚳ C/K 13, 6 ᚷ G 17, 7 ᚹ W 19, 8 ᚻ H 23, 9 ᚾ N 29, 10 ᛁ I 31, 11 ᛄ J 37, 12 ᛇ EO 41, 13 ᛈ P 43,
  14 ᛉ X 47, 15 ᛋ S/Z 53, 16 ᛏ T 59, 17 ᛒ B 61, 18 ᛖ E 67, 19 ᛗ M 71, 20 ᛚ L 73, 21 ᛝ NG/ING 79,
  22 ᛟ OE 83, 23 ᛞ D 89, 24 ᚪ A 97, 25 ᚫ AE 101, 26 ᚣ Y 103, 27 ᛡ IA/IO 107, 28 ᛠ EA 109.
- Solved: A Warning (Atbash); Welcome (Vigenere DIVINITY, 11 F-skips); Some Wisdom (plain, ends in
  a word/number square); Koan 1 (Atbash then +3); The Loss of Divinity (plain); Koan 2 (Vigenere
  FIRFUMFERENFE = CIRCUMFERENCE with C->F, 2 F-skips); An Instruction (plain, 5x5 square, rows sum
  3301); An End p56 (subtract prime_n - 1, one F-skip, reported as the 4th F); Parable p57 (plain).
  Every key came from the book's own plain pages. Every keyed solved section uses F-skips.
- Unsolved: 9 sections, 12,956 runes, 2,921 words. Section (pages, runes, doublets): p0-2 (729, 4),
  p3-7 (1,145, 6), p8-14 (1,729, 9), p15-22 (1,903, 10), p23-26 (1,021, 11), p27-32 (1,433, 13),
  p33-39 (1,680, 12), p40-53 (3,008, 18), p54-55 (308, 3). IoC 0.98-1.00 everywhere (random 1.0,
  English in runes ~1.78).
- The one fingerprint: 86 doublets in 12,947 adjacent pairs (0.66%; random 3.45%, ~446 expected).
  Step histogram c_i - c_(i-1) mod 29 for steps 0..28: 86, 459, 504, 440, 438, 446, 430, 470, 426,
  510, 497, 454, 449, 503, 474, 469, 448, 404, 433, 474, 467, 462, 421, 486, 467, 467, 457, 475, 431.
  Steps 1-28 are uniform and independent of the previous rune; lag-2 and lag-3 coincidences are
  normal; doublets fall on all runes, inside words (0.63%) and across gaps (0.80%), and are real
  glyphs on the images. Doublet suppression appears in plain reading order, so no transposition
  sits on top of the chain.
- No periodicity up to 300 per section or 600 overall; no shared keystream between sections at
  overlaps of 600+; mean word length 4.47 runes (solved pages 4.03), two-rune words 15.5%; one
  repeated 6-gram DJUBEI at corpus positions 6555 and 12950.
- Only known model that fits: a chain cipher, c_i = c_(i-1) + s_i with s_i in 1..28 from a flat,
  aperiodic key. So the problem is finding the key source.
- Cicada hints: 2016 signed message says LP is the way, its words are the map, their meaning the
  road, their numbers the direction. 2017 signed message: beware false paths, verify PGP 7A35090F.

PRIOR WORK (seed one ledger entry each; source = who)
- Monoalphabetic, Caesar, Atbash, affine, transposition: excluded by flat statistics (wiki, relikd,
  LiberPrimusAnalysis = LPA).
- Periodic Vigenere/Beaufort up to period 300/section and 600/corpus, with and without F-skips and
  skip-on-collision (LPA). relikd's interrupt database: key length <= 32, every rune as interrupter,
  first 20 interrupts, best IoC 1.3-1.4 (overfit).
- All 294k OEIS sequences, first 40 terms, small offsets, all shifts, F-skip combos (relikd);
  24 sequences x 200 offsets raw and 22 x 300 in chain form with 14 step orderings (LPA).
- Totient/prime streams; six prime-value feedback variants; ciphertext autokey lags 1-60, plaintext
  autokey lags 1-3 all seeds, inside the chain (LPA, relikd).
- Running keys: solved LP text and ciphertext, Self-Reliance, The Mabinogion, every offset (LPA).
- Word-level shifts, Playfair-style pairs (LPA; jbo's cicada_tools). Crib tool Cicada_Breaker (2016).
- OutGuess on all 75 page images, no key and 96 keys: only known 2014 payloads (LPA).
- The 2014 growing string and raw page-image bytes as running keys (LPA).
- Page-56 hash: 692k archive candidates (SHA-512, LPA); onion lists and numeric domains with
  SHA-512 and BLAKE2b (relikd). Never found; algorithm unconfirmed.
- Base-60 grid read in bases 58-63 (relikd).

THIS RUN (17 Oct 2026; all negative; controls passed)
- Key resets per word, sentence, line, page (any key), raw and chain: control z 5.6-6.1, real z
  -0.7..+1.0 (one z 3.0 in p54-55 is chance by permutation null).
- Page pairs sharing a key from their first rune: 7 pairs above z 3 = shuffled median 7.
- Nine sequences run backwards from each section end, 60 offsets, both signs, raw and chain:
  control 1.93, real 1.08-1.13.
- Shift arithmetic in Latin-alphabetical rune order, 24 keywords + sequences: control 1.76, real
  1.02-1.08.
- Perl drand48 int(rand(29))/int(rand(28)) and glibc rand()%29/%28, seeds 0..1,048,575 plus 22
  Cicada numbers, first 300 runes of each section, 4 forms: control 1.88 raw, 1.81 chain; best 1.23,
  falling to ~1.01 on full sections. Python MT seeds 0..262,143 (Py2 and Py3 mappings): same.
- 4,032 hash pads (96 Cicada words x MD5/SHA-1/SHA-256/SHA-512/SHA3-256/SHA3-512/BLAKE2b x digest
  chain/hex chain/counter x byte%29 or base-29 digits): control 1.88, best 1.16.
- Unused numbers in base 29 (P.S. number and factors, cookies, page-56 hash, parable number,
  845145127, 1231507051321, key id) as running keys: all below random 99th percentile.
- The 256-byte grid as running key, every offset, raw and chain, both directions: 1.16-1.18 vs
  random-key null 1.17-1.27.
- 2013 Cicada OS files (761.MP3, _560.00, 560.17, 560.13, wisdom = folly), forwards and reversed,
  every offset, raw form, LLR scoring: control +0.40/rune (English), best -0.28 to -0.47 (random
  mean -0.84).
- Doublets are not plaintext doubled letters (English doubles 3.49%, position chi2 255) and not one
  rare letter.
- Urquhart-style book code: the 256 grid numbers as word indices (0- and 1-based, direct and
  running sum) into LP's solved plaintext words, all unsolved cipher words, p40-53 and p54-55 words,
  first and last letters: English bigram score below the random-index 99th percentile everywhere;
  planted book-code control +0.35.

LEADS (unused clues)
- 8x32 grid of two-character tokens in section p40-53: digits 0-9A-Za-x, value = 60*first + second,
  gives 256 bytes spanning 0..255 (entropy 7.17; first bytes cbe7a7ba61ed7eb7). Not an RSA modulus
  (big-endian divisible by 2, 5, 43, 53).
- Page-56 hash: 36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fda
  f1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4.
- Page-15 square: 3258 3222 3152 3038 / 3278 3299 3298 2838 / 3288 3294 3296 2472 / 4516 1206 708
  1820 = 3301 +- primes whose prime indices are Fibonacci numbers (Zeckendorf spiral).
- Numbered list 1-5 in section p33-39 (like the Loss of Divinity list); a lone numeral 7 in p8-14;
  cuneiform numerals 1033 and 3301 in the p33-39 artwork.
- 2012 P.S. number (131 digits) = 99554414790940424414351515490472769096534141749790794321708050837 x
  104593961812606247801193807142122161186583731774511103180935025763 (both prime).
- 2013 cookies 167=6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6 and
  761=7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5.
- Telnet prime list missing 73..1223; prime-length space runs in 2012, 2014, 2015 signed messages;
  "9133" at the end of the 2014 onion 4 string; the never-visited 2012 Britannica onion.

BACKLOG (seed as B01..B11, ranked)
- B01 Skip-tolerant running-key engine: allow the key offset to drift by one at each candidate
  F-skip (dynamic programming over drift, or short windows at every position); planted control with
  skips; then re-run every text and file source already in the ledger.
- B02 Plaintext-reactive key rules (pointer moves by previous rune's prime, skip when output would
  repeat, etc.) over long key sources, hill-climbed with an n-gram model.
- B03 Public-domain Cicada texts as keys: Liber AL vel Legis (2013 book code), Britannica 1911
  "Cicada" article (2012), Blake's Marriage of Heaven and Hell (2012). Raw and chain, with B01.
- B04 Section titles as cribs: derive key fragments from plausible titles (p54-55 is "A" + 8 runes;
  solved titles are short phrases) and search candidate key sources for those fragments.
- B05 The 256-byte grid as ciphertext: raw OpenPGP packet, AES with LP-word keys, XOR with the
  page-56 hash and 2013 files; look for headers.
- B06 Other stego tools on page images (steghide, JPHide; OpenPuff needs Windows: write the password
  list and ask the human to run it); JPEG quantization tables; the fixed black dots.
- B07 Non-English plaintext scoring (Latin, Old English, number-heavy Runeglish).
- B08 The 86 doublet positions read as numbers (gaps, rune values, page positions).
- B09 Other arithmetic orders (rune-poem variants, primes under other moduli, the 2014 rearranged table).
- B10 Prime-Fibonacci keystreams in the style of the page-15 square and the 2016/2017 message sums.
- B11 Self-keyed book codes, the pattern Fable 5.1 used to crack Urquhart's 1653 ciphers (number k
  indexes a word in section or page k of the same book; take its first letter). Apply to every
  number LP prints (256-byte grid, page-15 square, numbered list, lone 7, magic squares on solved
  pages) indexing LP's own pages, lines, sentences or words, and to rune keys derived the same
  way. Simple global-index and running-sum variants are done (negative); page-, line- and
  sentence-indexed variants are open. Also read the 2016 hint "words are the map, numbers are the
  direction" this way.

PITFALLS (put in the lp-data skill)
- Blank lines are not reliable page breaks: p3-7, p15-22, p33-39 and p40-53 parse to the wrong
  page count. Use line counts or the page images.
- IoC maxima over millions of trials on 300-rune windows reach ~1.2-1.25 by chance; always re-score
  top hits on the whole section.
- Binomial tails with p = 1/29 are skewed; use permutation nulls, not normal z.
- Log-likelihood scoring needs letter identities (raw form only); the chain form needs IoC, since
  the step-to-letter mapping is unknown.
- A 2025 wiki note says every page hides OutGuess data; controlled runs show that is random LSB noise.

DONE MEANS: gate test passes; ledger has an entry for every item in PRIOR WORK and THIS RUN; eleven
backlog files; skills and skeptic agent written; build_index works; handoff note written; branch
pushed and a PR opened titled "Bootstrap the Liber Primus lab". Keep this session lean: do not
re-run the heavy sweeps, only the gate and one quick seed script to confirm the port.
```

---

## OpenAI helper v3 (paste once into a session; no key needed yet)

Replaces the earlier v2 upgrade prompt. Delete `OPENAI_MODEL` from the environment if it is there.

```text
Maintenance session, no experiments. This supersedes the earlier "OpenAI helper v2" prompt; if
parts of it already exist, update them to match. Follow CLAUDE.md (PascalCase, never print keys).

1. docs/models/openai.md, dated 17 Oct 2026 with source links. These models are newer than your
   training data: trust this file and the live model list over memory.
   - gpt-6-astra: OpenAI's flagship, released 3 Sep 2026. Effort low|medium|high|xhigh|max (none
     returns HTTP 400). 1.05M context, 128k max output, knowledge to 30 Apr 2026. Safety monitors
     can stop a request. It asks clarifying questions readily, so prompts tell it to answer anyway.
   - gpt-6.1-sol: released 29 Sep 2026, near-Astra quality at about a fifth of the price. Effort
     low|medium(default)|high|xhigh|max.
   - gpt-6-luna: cheapest and fastest. Effort none|low|medium(default)|high|xhigh|max.
   - gpt-5.6-sol: previous generation (Jul 2026).
   - Pro is a mode, not a model: "reasoning": {"mode": "pro"} in the Responses API, set
     independently of effort. Much slower and several times the tokens.
   - Hidden reasoning tokens are billed as output and count toward our cap. max_output_tokens
     bounds reasoning plus answer; if it runs out first, the response is "incomplete" with no answer.
   - Our limit is tokens, not dollars, so use gpt-6-astra. Use gpt-6.1-sol only when Astra stops a
     request or the key can't use Astra. Skip the others.
   - Refresh rule: if this file is over 30 days old, or --list-models shows an id it doesn't
     describe, look the model up (web search, developers.openai.com/api/docs/models) and update
     the file before using that model.
   Add to CLAUDE.md: "OpenAI models newer than your training exist. Read docs/models/openai.md
   before calling tools/ask_other_model.py."

2. Effort policy (in that file and in the lp-budget skill):
   - medium, max-output 16000: brainstorming lists of hypotheses.
   - high, max-output 25000: attacking a test design, hunting bugs, checking a claimed hit,
     writing an exact test spec.
   - xhigh, max-output 40000: the single hardest question of a phase.
   - pro mode (effort high, max-output 40000): at most once per project, final phase, 60k+ left.
   - Never max effort (one public run waited 7+ minutes for the first token) and never low or
     none (do small jobs yourself).

3. tools/ask_other_model.py, standard library only:
   - --list-models: GET /v1/models (no tokens); flag ids missing from docs/models/openai.md.
   - Base URL from OPENAI_BASE_URL (default https://api.openai.com/v1). Send an Authorization
     header only if OPENAI_API_KEY is set; otherwise the environment's API credential adds it.
   - Flags: --model (required), --prompt-file, --system-file, --purpose, --effort,
     --mode standard|pro, --max-output (default from the effort policy, hard max 48000),
     --dry-run, --use-reserve.
   - Every call: POST /v1/responses with "background": true, then poll GET /v1/responses/{id}
     every 15 s. Always prepend a developer message: "One-shot request from an automated research
     lab. You cannot ask questions. State any assumption and answer fully, concretely, testably."
   - Deadlines: medium 8 min, high 12, xhigh 20, pro 30. At the deadline, POST
     /v1/responses/{id}/cancel and read its usage; with no usage, count the whole reservation.
   - Pro fallback, the only automatic retry: if a pro call hits its deadline or fails, rerun it
     once in standard mode with the same model and effort, after a fresh budget check. Log both.
   - Stopped by a safety check: log status "flagged", don't retry that model, print a hint to ask
     gpt-6.1-sol instead. Incomplete: log it, keep any partial text, exit non-zero.
   - Budget: Cap = min(OPENAI_TOKEN_CAP or 230000, 230000) - 10000; Reserve = 50000, spendable
     only with --purpose verify or --use-reserve. Ledger budget/openai/ledger.jsonl, one entry per
     call with a unique id: time, branch, CLAUDE_CODE_REMOTE_SESSION_ID, model, mode, effort,
     purpose, input_tokens, output_tokens, reasoning_tokens, total_tokens, status. Before each
     call, git fetch origin main and merge origin/main's ledger with the local one by id.
   - Under an exclusive fcntl lock on budget/openai/ledger.lock: total the ledger, reserve
     prompt chars / 3 + max-output, refuse if that passes Cap (or Cap - Reserve without verify or
     --use-reserve), append a "reserved" entry, release the lock. After the call, append the final
     entry with the same id; it replaces the reservation in totals. Drop any per-branch rule.
   - Save prompt, reply and usage to docs/council/<date>/<NN>-<model>-<purpose>.md. Print only
     the remaining budget and that path.
   - Tests against a local mock server: completed, incomplete, failed, flagged, a pro call that
     never finishes (must fall back), cap and reserve refusals, two parallel calls. If a key or
     credential works, one live call: gpt-6-luna, effort none, max-output 200.

4. Agents. .claude/agents/council.md (model: sonnet; tools: Bash, Read, Write, Glob, Grep): makes
   ONE helper call from a brief the lead gives it and returns at most 15 lines, each testable idea
   as name, mechanism, why it fits the fingerprint, cheapest falsifying test; never runs
   experiments. .claude/agents/worker.md (model: sonnet): runs one claimed backlog item with
   lp-experiment, writes only its own ledger file and artifacts, stays until its long jobs
   finish. .claude/agents/skeptic.md: model fable.

5. .claude/skills/lp-council/SKILL.md with four phases. Each starts with --list-models and the
   refresh rule, runs in only one key-using session at a time, and ends with
   docs/council/<date>/README.md and lp-handoff. Briefs use rune numbers or Latin letters, never
   rune characters, and stay under 5,000 tokens.
   - kickoff (about 75k): brief.md with the fingerprint, solved methods, LEADS and the 15 biggest
     negative families. Two Astra calls at medium, one framed as a cryptanalyst and one as a
     puzzle designer in Cicada's style: "Give 12 concrete, testable constructions that would
     produce exactly this fingerprint, each with its cheapest falsifying test." Dedupe against the
     ledger and file the best as backlog items. Then one call at high: how could our 3 most
     important negative tests have missed a real signal?
   - midpoint (about 65k, after the first wave of results): bug hunt on the newest engine code at
     high, then fresh ideas starting from what failed and why.
   - final (about 30k plus whatever is left, the project's last week): whole-ledger review; the
     one pro question if 60k+ remains.
   - verify (the 50k reserve, any time a result beats its noise ceiling, after the skeptic): send
     the method, evidence, control and null and ask for an independent attack at high.

6. If a download is blocked by the network allowlist, add the domain to docs/NETWORK.md for the
   human; don't work around it.

7. Commit on a branch and open a PR titled "OpenAI helper v3: models, effort policy, council phases".
```

---

## Every later session: worker (paste, optionally naming an item)

```text
Run the lp-start skill. Work on backlog item <B0X, or "the top open item">. Follow lp-experiment
exactly: positive control first, null or noise ceiling, recheck top hits on full sections, record a
ledger YAML. Keep outputs short and checkpoint long jobs to disk. If you find anything above the
noise ceiling, run the skeptic agent on it before believing it. Finish with lp-handoff: ledger
entries, the item's status, a handoff note with what you'd do next and what not to repeat, rebuild
the index, push, and open a PR. If a step needs something only a human can do (Windows software,
a file), write it in the handoff and stop.
```

A wave is 2-3 separate sessions, each with one backlog item; merge their PRs before the next wave.
Do not fan one session out over several items. The worker subagent (`.claude/agents/worker.md`) is
only for helping within a session's own item, e.g. one variant or sub-sweep of it.

## Open-ended hunt (Fable 5.1, modeled on the Vals AI Urquhart run)

Vals AI's run that cracked the Cyphral Distich used an open goal, encouragement, a push to think
creatively, two constraints, and zero interjections (44 minutes, 176k tokens). It worked because the
key was inside the book that held the cipher, and the model went looking there. Use this prompt
once the ledger is in place; do not answer its questions mid-run unless it is blocked.

```text
Run lp-start. You have the whole repo and its ledger of what has failed. Your goal: find a key
source or method for the unsolved Liber Primus pages that the ledger has not covered. You have
solved hard problems before; approach this like a cryptanalyst and a historian at once. Every key
Cicada used on solved pages came from the book's own text, and their 2016 message says the book's
words are the map and its numbers the direction. Look for structure only a careful reader of the
whole book and puzzle history would notice, and test it. Constraints: do not repeat any ledger
family without a genuinely new variant, and stop pursuing a line when it stops budging. Every
claim needs a planted control. If you find a candidate plaintext, make it self-verifying: a
verify script anyone can run, a SOLUTION.md with the exact rule, and a skeptic-agent review.
Record everything with lp-experiment, then finish with lp-handoff.
```

## OpenAI council phases

After the v3 PR is merged and the key is added, run one phase per session. Never run two
key-using sessions at once, and merge each council PR before the next phase.

| Phase | When | Paste | Budget |
| --- | --- | --- | --- |
| kickoff | now | `Run the lp-council skill, kickoff phase.` | ~75k |
| midpoint | after the first 3-4 worker PRs are merged | `Run the lp-council skill, midpoint phase.` | ~65k |
| final | the last week before the Claude credits expire | `Run the lp-council skill, final phase.` | ~30k + leftovers |
| verify | when a result beats its noise ceiling and survives the skeptic | `Run the lp-council skill, verify phase, on <ledger id>.` | 50k held back |

Use Opus 5.5 or Fable 5.1 for these sessions. Workers test the new backlog items on Claude
credits and never touch the key.

## Review session (Fable 5.1, optional OpenAI second opinion)

```text
Run lp-start, then review every ledger entry added since the last review note in docs/sessions/.
For each: re-run its positive control, check the null, and look for alignment, leakage or
multiple-testing mistakes using the skeptic agent. If the OpenAI key is live and no other session
is using it, get an independent critique of the riskiest claims through tools/ask_other_model.py,
inside the cap. Then
re-rank docs/backlog/ with a short reason per change, add new items you believe are untried, and
finish with lp-handoff.
```
