import json
import os

import anthropic

MODEL = "claude-haiku-4-5-20251001"
MAX_ITEMS = 15


def summarize(data: dict) -> dict:
    items = data["items"][:MAX_ITEMS]
    if not items:
        return {"items": []}

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": _build_prompt(items)}],
    )

    raw = response.content[0].text if response.content else "[]"
    summaries = _parse_response(raw)
    for item, summary in zip(items, summaries):
        item["summary"] = summary
    return {"items": items}


def _build_prompt(items: list) -> str:
    lines = [
        "For each article below, write a 2-3 sentence English summary.",
        "What happened and why does it matter? Write for a technical audience.\n",
        'Respond only with JSON: [{"summary": "..."}, ...]\n',
        "Articles:\n",
    ]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['title']} ({item['source']})\n   {item['snippet']}\n")
    return "\n".join(lines)


def _parse_response(text: str) -> list[str]:
    start, end = text.find("["), text.rfind("]") + 1
    if start == -1 or end == 0:
        print(f"Summarizer: no JSON array in response; raw head: {text[:200]!r}")
        return []
    try:
        parsed = json.loads(text[start:end])
        return [e.get("summary", "Summary unavailable.") for e in parsed]
    except Exception as e:
        print(f"Summarizer: JSON parse failed ({e}); raw head: {text[:200]!r}")
        return []
