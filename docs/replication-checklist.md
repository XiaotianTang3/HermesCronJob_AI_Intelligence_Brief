# Replication checklist

Use this before claiming another Hermes agent has replicated the workflow.

## Installation

- [ ] `./install.sh` completed without error.
- [ ] `./verify.sh` completed without error.
- [ ] `~/.hermes/scripts/ai_daily_intelligence_probe.py` exists and is executable.
- [ ] All three skills exist under `~/.hermes/skills/`.

## Cron configuration

- [ ] Cron job name is `AI Daily Intelligence Brief` or equivalent.
- [ ] Cron attaches these skills:
  - `ai-daily-intelligence-brief`
  - `ai-news-briefing`
  - `ai-investment-briefing-workflow`
- [ ] Cron script is `ai_daily_intelligence_probe.py`.
- [ ] Toolsets include `terminal`, plus web/search/browser fallback if available.
- [ ] Delivery target is appropriate for the user (`origin`, email, Telegram, etc.).

## Output quality

- [ ] Every main bullet has at least one URL.
- [ ] Industry and investment sections are both present.
- [ ] Funding amounts/stages/investors are sourced or marked uncertain.
- [ ] Rumors / "in talks" items are separated from completed financings.
- [ ] The `Cross-Signals` section synthesizes industry + capital signals instead of repeating bullets.
- [ ] The brief is concise enough for the delivery channel.

## Failure modes

- If the probe returns many items but the brief has no URLs, tighten the cron prompt's source-link rule.
- If cron times out, reduce source counts in the probe scripts or send by email instead of chat.
- If China funding coverage is weak, add region-specific RSS/search sources and keep verification strict.
