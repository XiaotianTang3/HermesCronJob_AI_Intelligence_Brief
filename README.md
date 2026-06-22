# AI Daily Intelligence Brief for Hermes

A reusable Hermes cron kit for a combined daily AI intelligence briefing.

It merges two briefing streams into one scheduled report:

1. **AI Industry News** — model labs, product launches, platform moves, regulation, China/global competition, labor/industry impact.
2. **AI Investment & Funding** — AI startup financings, VC/investor moves, M&A, strategic investments, founder/company signals.

The kit is designed for other Hermes agents to install and adapt. It uses free/public sources by default. The only paid component is whatever LLM provider the Hermes agent already uses.

Default output is **Chinese**, matching the original use case. You can edit the cron prompt if you want English output.

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
git clone https://github.com/XiaotianTang3/HermesCronJob_AI_Intelligence_Brief.git
cd HermesCronJob_AI_Intelligence_Brief
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

### Copy-paste instruction for another Hermes agent

```text
Clone https://github.com/XiaotianTang3/HermesCronJob_AI_Intelligence_Brief, run ./install.sh and ./verify.sh, then create a recurring cron job using cron-templates/ai-daily-intelligence-brief.json. Preserve the attached skills, script, enabled_toolsets, source-link rule, and Chinese output format.
```

## Quality rules

- Every main bullet must include at least one clickable URL.
- Funding items should prefer official/company/investor announcements, then reputable media.
- Do not include old resurfaced stories as new.
- Do not mix rumors or "in talks" items into completed financings.
- Put important but unconfirmed leads under `待确认观察` / `Unconfirmed / Watch`.
- Fewer verified items are better than many weak items.

## Replication target

With the same Hermes version, model, tool availability, and network access, another agent should be able to produce a brief with very similar structure and source discipline. Exact article selection may vary because public RSS/search feeds change over time.

Run `docs/replication-checklist.md` before claiming replication success.

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
examples/
  output-shape.md
```

## Notes

- Public RSS and Google News RSS can change or rate-limit. The scripts use hard timeouts so a bad feed does not block the whole cron.
- This is intelligence/summarization infrastructure, not financial advice.

## Optional: Email Delivery via Resend
The updated prompt template includes an instruction to send the final brief via email using a local `send_ai_brief.py` script. 
To enable this:
1. Ensure you have a valid `RESEND_API_KEY` and target emails configured in `~/.hermes/.env` (e.g., `RESEND_TARGETS_01="your_email@example.com"`).
2. Ensure you have a `send_ai_brief.py` script in `~/.hermes/scripts/` capable of reading these environment variables and firing the Resend API.
3. If you do not want email delivery, simply remove the "特别任务（邮件订阅交付）" section from the `cron-templates/ai-daily-intelligence-brief.json` prompt before creating the job.
