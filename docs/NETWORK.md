# Network allowlist requests (for the human)

When a download or an API call is blocked by this environment's network allowlist, add a row here.
Don't work around the block with mirrors, other proxies or copied files. A human adds the domain in
the environment's network settings and then clears the row.

| date | domain | needed for | blocked by (error) | branch |
| --- | --- | --- | --- | --- |

Nothing is blocked as of 2026-10-18. These all work: api.openai.com (the credential is injected by the
proxy), developers.openai.com, and the hosts that `scripts/fetch_data.sh` uses.
