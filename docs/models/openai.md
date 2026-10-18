---
updated: 2026-10-17
---

# OpenAI models for the lab

These models are newer than Claude's training data. Trust this file and the live model list
(`python3 tools/ask_other_model.py --list-models`) over memory.

**Refresh rule.** If `updated:` above is over 30 days old, or `--list-models` shows an id this file
does not describe, look the model up (web search, developers.openai.com/api/docs/models) and update
this file before using that model. The tool refuses a model this file doesn't name, and refuses
everything once the file is over 30 days old.

## What we use

**gpt-6-astra.** Always use this one: our limit is tokens, not dollars, and Astra gives the most per token.
Use **gpt-6.1-sol** only when Astra stops a request (a safety check) or the key can't reach Astra.
Skip the other models.

| id | released | effort values | notes |
| --- | --- | --- | --- |
| gpt-6-astra | 3 Sep 2026 | low, medium, high, xhigh, max (none returns HTTP 400) | OpenAI's flagship. 1.05M context, 128k max output, knowledge cutoff 30 Apr 2026. Safety monitors can stop a request. Asks clarifying questions readily, so every prompt says to answer anyway (the tool's fixed developer message). |
| gpt-6.1-sol | 29 Sep 2026 | low, medium (default), high, xhigh, max | Close to Astra's quality at about a fifth of the price. 1.05M context, 128k output, knowledge cutoff 30 Apr 2026. Our fallback. |
| gpt-6-luna | (Sep 2026) | none, low, medium (default), high, xhigh, max | Cheapest and fastest; knowledge cutoff 18 May 2026. Used only for the tool's live smoke test. |
| gpt-5.6-sol | Jul 2026 | (not needed) | Previous generation. Not used. |

Ids that are live but not used (seen in `--list-models` on 2026-10-17): **gpt-6-sol** (the
GPT-6 Sol that gpt-6.1-sol replaced), and **gpt-5.6-luna** and **gpt-5.6-terra** (the rest of the
previous generation). Skip them. Older ids (gpt-5.x and earlier, o-series) and non-text models
(image, realtime, transcribe, tts) are outside the tool's check and are not used.

## Mechanics that cost tokens

- **Pro is a mode, not a model.** Send `"reasoning": {"mode": "pro"}` in the Responses API. It is set
  separately from effort. It is much slower and uses several times the tokens.
- **Hidden reasoning tokens are billed as output** and count toward our cap. `max_output_tokens`
  bounds reasoning and answer together. If reasoning uses it all first, the response is `incomplete`
  (`incomplete_details.reason = max_output_tokens`) and has no answer, but the tokens are still spent.
- **Background mode.** `"background": true`, then poll `GET /v1/responses/{id}` while the status is
  `queued` or `in_progress`. `POST /v1/responses/{id}/cancel` stops the request, and calling it twice
  is harmless. The docs don't say whether a cancel returns usage, so the tool counts the whole
  reservation whenever usage is missing.
- **Safety stops.** The docs don't pin down how a safety stop is reported. The tool logs a request as
  `flagged` when its error code or message, or its incomplete reason, mentions safety, a content
  filter, a usage policy, `invalid_prompt`, moderation or cyber.

## Effort policy

| use | effort | max-output |
| --- | --- | --- |
| brainstorming lists of hypotheses | medium | 16000 |
| attacking a test design, hunting bugs, checking a claimed hit, writing an exact test spec | high | 25000 |
| the single hardest question of a phase | xhigh | 40000 |
| pro mode: at most once per project, final phase, only with 60k+ left | high (+ mode pro) | 40000 |

- Never use max effort. One public run waited over 7 minutes for its first token. The tool refuses it.
- Never use low or none. Do small jobs yourself. The tool refuses them unless `--max-output` is
  given; that exception exists only for the smoke test.
- Deadlines: medium 8 min, high 12, xhigh 20, pro 30. At the deadline the tool cancels the request.
  A pro call that times out or fails is rerun once in standard mode at the same effort.
- Hard limit on `--max-output`: 48000.

## Budget

Cap = min(`OPENAI_TOKEN_CAP` or 230000, 230000) - 10000 = 220000 tokens for the whole project. That
includes a 50000-token reserve, which only `--purpose verify` or `--use-reserve` can spend. The
shared ledger is `budget/openai/ledger.jsonl`. It merges by id with origin/main before every call,
and git merges it with the union driver (`.gitattributes`).

## Sources

- https://developers.openai.com/api/docs/models — ids, context, max output, cutoffs, effort values
  (fetched 2026-10-17).
- https://developers.openai.com/api/docs/guides/reasoning — `reasoning.mode = pro`; Astra rejects
  `none`; 6.1 Sol defaults to medium; reasoning counts inside `max_output_tokens`; `incomplete` status.
- https://developers.openai.com/api/docs/guides/background — background mode, polling, cancel.
- Release dates and pricing ratio come from the lab's brief and from third-party write-ups. They are
  not on OpenAI's pages above:
  https://docs.apiyi.com/en/news/gpt-6-astra-launch,
  https://www.iweaver.ai/blog/gpt-6-1-sol-vs-astra-vs-luna/,
  https://www.developersdigest.tech/blog/gpt-6-in-7-minutes.
  The API's `created` stamps (gpt-6-astra 27 Aug, gpt-6-sol and gpt-6-luna 14 Sep, gpt-6.1-sol
  27 Sep, gpt-5.6-* 23 Jun 2026) fall just before those release dates.
