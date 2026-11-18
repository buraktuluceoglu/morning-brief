# morning-brief

A token-efficient daily news briefing pipeline. Fetches RSS feeds across AI and cybersecurity sources, filters by interest keywords, deduplicates against sent history, summarizes with Claude, and delivers a morning email via Gmail SMTP.

Runs automatically every day at 07:45 Turkish time (04:45 UTC) via GitHub Actions.

## Pipeline

```
RSS feeds → collector → filter → dedupe → cluster → summarizer → mailer
```

Each stage passes a JSON envelope to the next:

```json
{
  "items": [
    {
      "title": "string",
      "url": "string",
      "source": "string",
      "published_at": "ISO8601",
      "snippet": "string (max 300 chars)"
    }
  ]
}
```

## Agents

| Agent | Role | LLM? |
|---|---|---|
| `collector.py` | Fetches RSS feeds, normalizes URLs, trims snippets | No |
| `filter.py` | Keyword-matches items against `interests.md` | No |
| `dedupe.py` | Skips URLs already in `vault/sent_urls.json` | No |
| `cluster.py` | Groups near-duplicate stories on the same topic | No |
| `summarizer.py` | Sends filtered items to Claude Haiku for 2-3 sentence summaries | Yes |
| `mailer.py` | Sends HTML email via Gmail SMTP | No |

Only `summarizer.py` calls the LLM. It receives at most 15 items; each item is title + snippet (≤ 300 chars), never full article text.

## Sources

**AI**
- Anthropic News
- The Batch (deeplearning.ai)
- Simon Willison's blog
- HuggingFace Blog

**Cybersecurity**
- The Hacker News
- BleepingComputer
- Hacker News (news.ycombinator.com)

**Research**
- arXiv cs.AI
- arXiv cs.CR

Interest filtering rules live in [`interests.md`](interests.md).

## Setup

### Requirements

```
feedparser==6.0.11
anthropic>=0.40.0
```

Install:

```bash
pip install -r requirements.txt
```

### Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude Haiku |
| `GMAIL_USER` | Gmail address to send from |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your account password) |
| `RECIPIENT_EMAIL` | Address to send the brief to (defaults to `GMAIL_USER`) |

### Run locally

```bash
python main.py
```

## GitHub Actions

The workflow at `.github/workflows/daily.yml` commits the updated `vault/sent_urls.json` back to the repo after each successful run so the deduplication history persists across runs.

Secrets required: `ANTHROPIC_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`.

### Scheduling

GitHub's built-in `schedule` trigger is often delayed by several hours, so the primary trigger is an external cron service ([cron-job.org](https://cron-job.org)) that calls the `workflow_dispatch` API at 04:45 UTC. The GitHub `schedule` (also 04:45 UTC) stays as a fallback. If a brief was already sent today (a vault commit exists for today's UTC date), the workflow skips, so only one mail goes out per day.

Setup:

1. Create a fine-grained personal access token at GitHub → Settings → Developer settings → Fine-grained tokens, scoped to this repository only, with **Actions: Read and write** permission.
2. On cron-job.org, create a job:
   - URL: `https://api.github.com/repos/buraktuluceoglu/morning-brief/actions/workflows/daily.yml/dispatches`
   - Schedule: every day at 07:45, timezone `Europe/Istanbul`
   - Request method: `POST`
   - Headers: `Authorization: Bearer <TOKEN>`, `Accept: application/vnd.github+json`
   - Body: `{"ref":"main"}`
3. A successful call returns `204 No Content`. Renew the token before it expires.

## Vault

`vault/sent_urls.json` tracks URLs that have already been emailed. URLs are written only after a successful send. Entries older than 30 days are pruned automatically. URL comparison is exact-match after normalization (trailing slash stripped, query params removed).
