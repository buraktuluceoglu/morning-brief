# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## 5. Project: morning-brief

**What this project does:**
A token-efficient daily news briefing pipeline. Fetches RSS feeds, filters by interests, deduplicates against sent history, summarizes with Claude, and sends a morning email via Gmail SMTP.

**Stack:**
- Python 3.10+
- feedparser — RSS okuma
- anthropic — Claude API (summarizer agent)
- smtplib — Gmail SMTP mail gönderme
- GitHub Actions — her sabah 08:00'de otomatik çalışma (05:00 UTC)

**Project structure:**
```
news-bot/
├── CLAUDE.md
├── interests.md        # Filtreleme kuralları
├── agents/
│   ├── collector.py    # RSS feed okuma
│   ├── filter.py       # interests.md'ye göre filtreleme
│   ├── dedupe.py       # Daha önce gönderilenleri ele
│   ├── summarizer.py   # Claude ile özetleme
│   └── mailer.py       # Gmail SMTP
├── vault/
│   └── sent_urls.json  # Gönderilen URL geçmişi
├── main.py             # Ana orkestratör
├── requirements.txt
└── .github/
    └── workflows/
        └── daily.yml
```

**Agent sorumlulukları:**
- `collector.py` → Sadece RSS okur, başlık + URL + snippet döndürür. LLM çağrısı yok.
- `filter.py` → interests.md'yi okur, keyword eşleşmesi yapar. LLM çağrısı yok.
- `dedupe.py` → sent_urls.json ile karşılaştırır. LLM çağrısı yok.
- `summarizer.py` → Sadece bu agent Claude'u çağırır. Input: filtrelenmiş haberler. Output: özet metin.
- `mailer.py` → Gmail SMTP ile mail gönderir. LLM çağrısı yok.

**Token kuralları — kritik:**
- Collector, filter ve dedupe agent'ları LLM çağrısı YAPAMAZ. Bu işler deterministik Python ile yapılır.
- Summarizer'a sadece filtrelenmiş ve dedupe edilmiş haberler gönderilir — ham RSS içeriği asla.
- Her haber için summarizer'a gönderilen input: başlık + snippet (max 300 karakter). Tam makale içeriği asla.
- Summarizer output'u: her haber için max 3 cümle özet.
- Günlük max haber sayısı: 15. Daha fazlası varsa en yenileri öncelikli.

**Veri akışı:**
```
RSS feeds → collector → filter → dedupe → summarizer → mailer
```
Her aşama JSON döndürür. Aşamalar arası veri formatı:
```json
{
  "items": [
    {
      "title": "string",
      "url": "string",
      "source": "string",
      "published_at": "ISO8601",
      "snippet": "string (max 300 char)"
    }
  ]
}
```

**RSS Feed listesi:**
```
# Yapay Zeka
https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml  # Anthropic News
https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/deeplearning_the_batch_rss.xml  # The Batch
https://simonwillison.net/atom/everything  # Simon Willison
https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/huggingface_blog_rss.xml  # HuggingFace Blog

# Siber Güvenlik
https://feeds.feedburner.com/TheHackersNews  # The Hacker News
https://krebsonsecurity.com/feed  # Krebs on Security
https://bleepingcomputer.com/feed  # BleepingComputer
https://darkreading.com/rss.xml  # Dark Reading

# Araştırma
https://export.arxiv.org/rss/cs.AI  # arXiv cs.AI
https://export.arxiv.org/rss/cs.CR  # arXiv cs.CR
```

Not: Anthropic ve The Batch feed'leri GitHub tabanlı — repo güncellenmezse durabilir.

**Vault / dedupe kuralları:**
- sent_urls.json'a sadece başarıyla gönderilen mail sonrası yaz.
- 30 günden eski URL'leri otomatik temizle.
- URL karşılaştırması exact match — normalize et (trailing slash, query params temizle).

**Gmail SMTP kuralları:**
- Şifre ve API key'ler asla koda yazılmaz. Environment variable kullan.
- Gönderim başarısızsa hata logla, programı crash ettirme.
- Mail formatı HTML — okunabilir, sade.

**GitHub Actions kuralları:**
- Her gün 05:00 UTC'de çalışır (Türkiye saatiyle 08:00, UTC+3).
- sent_urls.json her çalışma sonrası commit'lenir — geçmiş korunur.
- Secrets: ANTHROPIC_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD

**Yapma:**
- Collector/filter/dedupe'ye LLM çağrısı ekleme.
- Tam makale içeriğini Claude'a gönderme.
- Şifreleri koda yazma.
- 15'ten fazla haberi summarizer'a gönderme.
- sent_urls.json'u mail göndermeden önce güncelleme.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.