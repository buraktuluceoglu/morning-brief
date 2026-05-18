import re
from pathlib import Path

INTERESTS_PATH = Path(__file__).parent.parent / "interests.md"

SECTION_PRIORITY = {"Core focus": 3, "Adjacent": 2, "Research signals": 1, "Skip": -1}

_SECURITY_TOPICS = {
    "web application security", "offensive security",
    "vulnerability management", "malware", "data breaches",
}


def _parse_interests() -> list[tuple[str, str, list[str]]]:
    """Returns [(section, topic, [keywords])]."""
    entries = []
    current_section = None
    for line in INTERESTS_PATH.read_text().splitlines():
        m = re.match(r"^## (.+)", line)
        if m:
            current_section = m.group(1).strip()
            continue
        m = re.match(r"^- (.+)", line)
        if m and current_section:
            raw = m.group(1)
            topic, _, kw_str = raw.partition(" — ")
            topic = topic.strip()
            keywords = [k.strip().lower() for k in re.split(r"[,，]", kw_str or raw)]
            keywords.append(topic.lower())
            entries.append((current_section, topic, keywords))
    return entries


def _email_category(section: str, topic: str) -> str:
    if section == "Core focus":
        return "security" if any(t in topic.lower() for t in _SECURITY_TOPICS) else "ai"
    if section == "Adjacent":
        return "adjacent"
    if section == "Research signals":
        return "research"
    return "other"


def filter_items(data: dict) -> dict:
    interests = _parse_interests()
    scored = []
    for item in data["items"]:
        haystack = (item["title"] + " " + item["snippet"]).lower()
        best_score = 0
        best_category = None
        skip = False
        for section, topic, keywords in interests:
            priority = SECTION_PRIORITY.get(section, 0)
            if priority < 0:
                if any(re.search(r"\b" + re.escape(kw) + r"\b", haystack) for kw in keywords):
                    skip = True
                    break
                continue
            hits = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", haystack))
            if hits > 0:
                score = priority * hits
                if score > best_score:
                    best_score = score
                    best_category = _email_category(section, topic)
        if not skip and best_score > 0:
            scored.append({**item, "score": best_score, "category": best_category})
    scored.sort(key=lambda x: x["published_at"], reverse=True)
    return {"items": scored}
