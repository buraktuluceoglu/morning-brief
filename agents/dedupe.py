import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT = Path(__file__).parent.parent / "vault" / "sent_urls.json"
RETENTION_DAYS = 30


def _load() -> dict:
    if not VAULT.exists():
        return {}
    try:
        return json.loads(VAULT.read_text())
    except Exception as e:
        print(f"Vault corrupted [{VAULT}]: {e} — starting fresh")
        return {}


def dedupe(data: dict) -> dict:
    sent = _load()
    fresh = [item for item in data["items"] if item["url"] not in sent]
    return {"items": fresh}


def write_vault(data: dict) -> None:
    vault = _load()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).isoformat()
    vault = {url: ts for url, ts in vault.items() if ts >= cutoff}
    now = datetime.now(timezone.utc).isoformat()
    for item in data["items"]:
        vault[item["url"]] = now
    VAULT.write_text(json.dumps(vault, indent=2, ensure_ascii=False))
