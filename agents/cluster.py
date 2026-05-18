import re

_STOPWORDS = {
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
    "is", "are", "was", "were", "with", "that", "this", "it", "as", "by",
    "be", "has", "have", "how", "what", "when", "new", "use", "using",
    "can", "from", "its", "via", "not", "but", "after", "over",
}

SIMILARITY_THRESHOLD = 0.4


def _words(title: str) -> set[str]:
    tokens = re.sub(r"[^a-z0-9 ]", " ", title.lower()).split()
    return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}


def _jaccard(t1: str, t2: str) -> float:
    w1, w2 = _words(t1), _words(t2)
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def cluster(data: dict) -> dict:
    # items are score-sorted; keep the first (best) representative of each topic cluster
    kept: list[dict] = []
    for item in data["items"]:
        if not any(_jaccard(item["title"], k["title"]) >= SIMILARITY_THRESHOLD for k in kept):
            kept.append(item)
    return {"items": kept}
