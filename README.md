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
- Krebs on Security
- BleepingComputer
- Dark Reading

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

The workflow at `.github/workflows/daily.yml` runs on a cron schedule and commits the updated `vault/sent_urls.json` back to the repo after each successful run so the deduplication history persists across runs.

Secrets required: `ANTHROPIC_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`.

## Vault

`vault/sent_urls.json` tracks URLs that have already been emailed. URLs are written only after a successful send. Entries older than 30 days are pruned automatically. URL comparison is exact-match after normalization (trailing slash stripped, query params removed).
