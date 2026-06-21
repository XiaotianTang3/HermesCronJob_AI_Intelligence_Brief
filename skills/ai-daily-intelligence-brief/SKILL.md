---
name: ai-daily-intelligence-brief
description: Combined daily AI intelligence briefing for Hermes cron. Uses separate RSS probes for AI industry news and AI investment/funding, then verifies, deduplicates, ranks, and synthesizes a Chinese or English daily brief with source URLs.
type: workflow
---

# AI Daily Intelligence Brief

Use this skill when creating or running a combined daily AI briefing that covers:

1. AI industry/business news: major labs, product launches, platform moves, regulation, China/global competition, labor/industry impact.
2. AI startup investment news: financing rounds, VC/investor moves, M&A, strategic investment, founder/company signals.

The core pattern is:

```text
bounded RSS/search probes -> candidate leads -> source verification -> dedupe -> relevance ranking -> synthesis
```

## Non-negotiables

- Probe output is only candidate leads, not final truth.
- Every main bullet must include at least one clickable source URL.
- Important funding bullets should include two URLs when possible: official/company/investor source first, reputable media second.
- If a candidate lacks a verifiable URL, has stale dates, or only appears in low-quality aggregators, drop it or put it under "Unconfirmed / Watch".
- Do not pad. Fewer verified items are better than more weak items.
- This is market/industry intelligence, not investment advice.

## Recommended cron structure

Use one cron job with one combined pre-run script:

- `scripts/ai_daily_intelligence_probe.py` runs:
  - `ai_news_rss_probe.py`
  - `ai_investment_rss_probe.py`
- The cron prompt asks the agent to verify and synthesize both sections.
- Attach these skills:
  - `ai-daily-intelligence-brief`
  - `ai-news-briefing`
  - `ai-investment-briefing-workflow`

## Output format

```markdown
# AI Daily Intelligence Brief｜YYYY-MM-DD

2-4 sentence executive overview.

## 1. AI Industry News
- [Date] Event title — 2-3 sentences: what happened, why it matters, product/business/market implication. Source: URL1; URL2 if useful. Confidence: High/Medium/Low.

## 2. AI Investment & Funding
- [Date] Company/project raised/completed/reported [amount/stage] — investors, founder/team when available, business direction, why it matters. Source: URL1; URL2 if useful. Confidence: High/Medium/Low.

## 3. Cross-Signals
- 3-5 bullets connecting industry moves with capital allocation.

## 4. Watch Items: Next 1-4 Weeks
- 3-5 concrete items to monitor.

## 5. Unconfirmed / Watch
- Important but unconfirmed items, with candidate URL if available and clear uncertainty label.
```

## Quality checklist

Before final output:

- [ ] Every main bullet has at least one URL.
- [ ] Funding amount/stage/investors are sourced or marked undisclosed/uncertain.
- [ ] Old resurfaced stories are removed.
- [ ] Rumors / "in talks" / "reportedly" items are not mixed with completed financings.
- [ ] No source is represented as official unless it is actually official.
- [ ] The synthesis says what the combined industry + capital signal means.
