import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_SECTION_ORDER = ["ai", "security", "research", "adjacent"]
_SECTION_LABELS = {
    "ai": "Yapay Zeka & Araçlar",
    "security": "Siber Güvenlik",
    "research": "Araştırma",
    "adjacent": "Diğer",
}


def send_mail(data: dict) -> bool:
    items = data["items"]
    if not items:
        print("No items — skipping mail.")
        return False

    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("RECIPIENT_EMAIL") or user

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Morning Brief — {datetime.now(timezone.utc).strftime('%d %B %Y')}"
    msg["From"] = user
    msg["To"] = recipient
    msg.attach(MIMEText(_render_html(items), "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        print(f"Mail sent → {recipient} ({len(items)} items)")
        return True
    except Exception as e:
        print(f"Mail failed: {e}")
        return False


def _render_html(items: list) -> str:
    by_section: dict[str, list] = {}
    for item in items:
        by_section.setdefault(item.get("category", "adjacent"), []).append(item)

    sections_html = ""
    for key in _SECTION_ORDER:
        section_items = by_section.get(key, [])
        if not section_items:
            continue
        cards = "".join(_card(i) for i in section_items)
        sections_html += f'<div class="section"><h2>{_SECTION_LABELS[key]}</h2>{cards}</div>'

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body{{font-family:-apple-system,Arial,sans-serif;max-width:680px;margin:0 auto;padding:20px;color:#1a1a1a;background:#f5f5f5}}
  h1{{font-size:22px;border-bottom:2px solid #111;padding-bottom:8px;margin-bottom:4px}}
  h2{{font-size:12px;font-weight:700;color:#666;text-transform:uppercase;letter-spacing:.08em;margin:28px 0 10px}}
  .card{{background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:14px 16px;margin-bottom:8px}}
  .card a{{font-size:15px;font-weight:600;color:#0366d6;text-decoration:none}}
  .card a:hover{{text-decoration:underline}}
  .meta{{font-size:12px;color:#999;margin:3px 0 8px}}
  .summary{{font-size:14px;line-height:1.6;color:#333;margin:0}}
  .footer{{font-size:11px;color:#bbb;margin-top:32px;text-align:center}}
</style>
</head>
<body>
<h1>Morning Brief</h1>
{sections_html}
<p class="footer">morning-brief · {date_str}</p>
</body>
</html>"""


def _card(item: dict) -> str:
    summary = item.get("summary") or item.get("snippet", "")
    date = item.get("published_at", "")[:10]
    return (
        f'<div class="card">'
        f'<a href="{item["url"]}">{item["title"]}</a>'
        f'<div class="meta">{item["source"]} · {date}</div>'
        f'<p class="summary">{summary}</p>'
        f"</div>"
    )
