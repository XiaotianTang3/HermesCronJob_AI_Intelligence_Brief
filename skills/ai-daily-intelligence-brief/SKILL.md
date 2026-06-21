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

2-4 句总览：今天最重要的行业/资本共同信号是什么。

## 1. AI 行业动态
- [月日] 事件标题 — 2-3 句解释谁做了什么、为什么重要、对产品/商业/竞争格局意味着什么。来源：URL1；URL2（如有）。置信度：高/中/低。

## 2. AI 投融资动态
- [月日] 公司/项目 完成/传出 [金额/轮次/未披露] — 投资方、创始人/团队（可得则写）、方向、为什么重要。来源：URL1；URL2（如有）。置信度：高/中/低。

## 3. 交叉信号解读
- 3-5 条，把行业新闻和投融资动态放在一起判断。

## 4. 接下来 1-4 周看什么
- 3-5 条具体 watch items。

## 5. 待确认观察
- 重要但未确认的线索，明确标注不确定性，并尽量给候选 URL。
```

## Quality checklist

Before final output:

- [ ] Every main bullet has at least one URL.
- [ ] Funding amount/stage/investors are sourced or marked undisclosed/uncertain.
- [ ] Old resurfaced stories are removed.
- [ ] Rumors / "in talks" / "reportedly" items are not mixed with completed financings.
- [ ] No source is represented as official unless it is actually official.
- [ ] The synthesis says what the combined industry + capital signal means.
