# AI Daily Intelligence Brief for Hermes

A reusable Hermes cron kit for a combined daily AI intelligence briefing.

It merges two briefing streams into one scheduled report:

1. **AI Industry News** — model labs, product launches, platform moves, regulation, China/global competition, labor/industry impact.
2. **AI Investment & Funding** — AI startup financings, VC/investor moves, M&A, strategic investments, founder/company signals.

The kit is designed for other Hermes agents to install and adapt. It uses free/public sources by default. The only paid component is whatever LLM provider the Hermes agent already uses.

## How it works

```text
ai_daily_intelligence_probe.py
├── ai_news_rss_probe.py          # candidate AI industry/news leads
└── ai_investment_rss_probe.py    # candidate AI funding/investment leads

Hermes cron agent
├── verifies source/date/facts
├── deduplicates and ranks
├── drops weak/old/unverified items
└── writes the final daily brief with source URLs
```

The probe scripts are **not the final source of truth**. They only collect candidate leads. The Hermes agent must still verify each item before including it.

## Install

```bash
git clone <your-repo-url>
cd ai-daily-intelligence-brief
./install.sh
./verify.sh
```

This copies:

- `skills/*` → `~/.hermes/skills/`
- `scripts/*.py` → `~/.hermes/scripts/`

If you use a custom Hermes home, set `HERMES_HOME`:

```bash
HERMES_HOME=/path/to/.hermes ./install.sh
```

## Create the cron job

Use `cron-templates/ai-daily-intelligence-brief.json` as the source of truth.

Recommended fields:

```json
{
  "name": "AI Daily Intelligence Brief",
  "schedule": "25 10 * * *",
  "skills": [
    "ai-daily-intelligence-brief",
    "ai-news-briefing",
    "ai-investment-briefing-workflow"
  ],
  "script": "ai_daily_intelligence_probe.py",
  "enabled_toolsets": ["terminal", "browser", "web", "search", "file", "code_execution"],
  "deliver": "origin"
}
```

If you are creating it from another Hermes agent, ask that agent to read the JSON template and call its cronjob tool/API with those fields.

## Quality rules

- Every main bullet must include at least one clickable URL.
- Funding items should prefer official/company/investor announcements, then reputable media.
- Do not include old resurfaced stories as new.
- Do not mix rumors or "in talks" items into completed financings.
- Put important but unconfirmed leads under `Unconfirmed / Watch`.
- Fewer verified items are better than many weak items.

## Files

```text
skills/
  ai-daily-intelligence-brief/
  ai-news-briefing/
  ai-investment-briefing-workflow/
scripts/
  ai_daily_intelligence_probe.py
  ai_news_rss_probe.py
  ai_investment_rss_probe.py
cron-templates/
  ai-daily-intelligence-brief.json
docs/
  replication-checklist.md
  public-release-checklist.md
```

## Notes

- The default output prompt is English-language internally, but the title format is easy to localize. Edit the cron prompt if you want Chinese output.
- Public RSS and Google News RSS can change or rate-limit. The scripts use hard timeouts so a bad feed does not block the whole cron.
- This is intelligence/summarization infrastructure, not financial advice.
