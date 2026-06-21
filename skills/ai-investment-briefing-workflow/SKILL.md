---
name: ai-investment-briefing-workflow
description: Use this whenever the user asks for a daily/periodic AI investment brief, AI funding news, VC/angel rounds, China/global AI startup financing, investor-to-founder/company tracking, or wants a concise date-led AI financing digest. Enforces first-hand source priority, cross-validation, low-confidence labels, China+global coverage, and concise Telegram-ready bullets.
type: workflow
---

# AI Investment Briefing Workflow

Use this skill to produce concise AI investment/funding briefs with source discipline. The user prefers date-led bullets covering global + China, VC/angel rounds, investors -> AI startups/founders, and cross-validated priority.

## Core stance

Funding briefs are easy to pollute with recycled news, vague rumors, and duplicate syndications. Prioritize first-hand sources and label uncertainty. Do not invent amounts, investors, dates, founders, or round stages.

## Default scope

Unless the user says otherwise:
- the usere window: last 72 hours for the user's recurring daily cron brief; use an explicitly requested date range when provided. For one-off/manual daily briefs, clarify only if the window materially affects the answer; otherwise state the assumed window.
- Geography: global + China.
- Company type: AI-native startups, AI infrastructure, model labs, AI applications, robotics/autonomy with AI core, data/compute tooling for AI.
- Financing types: angel, seed, pre-A, A/B/C+, strategic investment, M&A only if AI-startup relevant.
- Exclude: generic tech funding with weak AI relevance, stock market moves, crypto token news unless directly AI infrastructure.

## Source priority

Use this order:

1. First-hand company/investor announcement
- company blog/newsroom
- investor blog/portfolio announcement
- founder post on X/LinkedIn/WeChat if credible
- SEC/official filing when relevant

2. Reputable reporting
- The Information, Bloomberg, Reuters, WSJ, TechCrunch, Fortune, Forbes, Sifted, DealStreetAsia, 36Kr, 投中网, 财新, 晚点, 机器之心, 量子位, 甲子光年, 明亮公司 etc.

3. Aggregators/databases
- Crunchbase, PitchBook summaries, IT桔子, 企查查, 天眼查, Dealroom, newsletters.

Use aggregators for discovery, not final authority, unless no better source exists.

## Verification rule

For each funding event, try to confirm:
- company name,
- date of announcement,
- round stage,
- amount and currency,
- investors,
- business/product category,
- founder or leadership if relevant,
- source URL.

Confidence labels:
- High: first-hand source or two reputable independent sources agree.
- Medium: one reputable report, or first-hand source missing amount/stage.
- Low: aggregator/social-only or conflicting details. Include only if strategically important, clearly labeled.

## Deduplication

Merge items when they refer to the same company + round + announcement date. If reports disagree, use this format:
- Amount: reported as [$X] by [source]; company did not disclose / another source says [$Y].

Do not count old rounds resurfaced by newsletters as new funding.

## Brief format

Default output should be Telegram-friendly and concise:

```text
AI 投融资简报｜YYYY-MM-DD

全球
- [Date] [Company] raised [amount/stage] from [investors]. Focus: [one-line AI category]. Source: [source name]. Confidence: [High/Medium/Low].

中国
- [Date] [Company/中文名] completed [amount/stage] from [investors]. Direction: [one-line]. Source: [source]. Confidence: [High/Medium/Low].

值得关注
- [1-3 bullets on investor pattern, category heat, founder/company signal]

未确认/低置信
- [Only if needed]
```

If there are no strong events, say so and include only confirmed notable items. Do not pad.

## Analysis layer

After raw funding bullets, add 1-3 concise pattern bullets:
- Which categories got capital? model infra, agents, AI apps, robotics, data, chips, devtools.
- Which investors are active?
- Any China/global divergence?
- Any founder/team signal?
- Any strategic investor signal?

Avoid generic “AI remains hot.” Name the actual pattern.

## Workflow nodes

Use this orchestration when doing a serious brief:

1. Discovery
Search recent funding news across global and Chinese sources. Output candidate events.

Practical discovery tactics when normal web search is weak, blocked, or unavailable:
- First get the live date/time with `date` so the 24h/72h window is explicit.
- Google Search may trigger bot blocks in browser; Bing may switch to localized/low-quality results. If that happens, use Google News RSS from terminal with `requests` or `curl`:
  - Global feed: `https://news.google.com/rss/search?q=<urlencoded query>&hl=en-US&gl=US&ceid=US:en`
  - China feed: `https://news.google.com/rss/search?q=<urlencoded query>&hl=zh-CN&gl=CN&ceid=CN:zh-Hans`
  - Useful query patterns: `AI startup funding when:3d`, `"AI" "raises" "funding" startup when:3d`, `"AI agent" funding when:3d`, `"AI" "Series A" funding when:3d`, `人工智能 完成 融资 when:3d`, `大模型 融资 when:3d`, `智能体 融资 when:3d`, `AI 融资 亿元 when:3d`.
- For candidate verification, search exact announcement titles in DuckDuckGo HTML (`https://html.duckduckgo.com/html/?q=...`) to find direct Business Wire/PR Newswire/company/investor/media URLs instead of relying only on Google News redirect links.
- Press-release sites often work better via their own search pages than via generic search:
  - PR Newswire search is reliable and parsable: `https://www.prnewswire.com/search/news/?keyword=<urlencoded exact title>`; extract the actual `/news-releases/...-<numeric-id>.html` URL from the search results, then parse title/meta description/body snippets for amount, round, lead investor, founders, and participants. Do not guess PR Newswire numeric IDs from slugs — the wrong ID returns 404 even when the title is correct. If terminal requests to PR Newswire return 403, resolve the Google News RSS wrapper with `browser_navigate`, then inspect `location.href` and navigate the resulting PR Newswire URL in the browser; the page body is often readable there even when `urllib` is blocked.
  - Business Wire may time out or block; first discover its exact URL through Google News RSS / DuckDuckGo / publisher mirrors, then retry with a long timeout. If still blocked, use a reputable mirror plus another independent source rather than burning time.
- Terminal/RSS parsing pitfalls:
  - On macOS system Python, `requests` may emit `urllib3 NotOpenSSLWarning` before XML output, which breaks `xml.etree.ElementTree.fromstring()` and can make Google News RSS look empty. Run Python snippets with `python3 -W ignore`, or strip everything before the first `<?xml` before parsing.
  - For Chinese pages with mojibake, set `r.encoding = r.apparent_encoding` before stripping HTML; 投资界/部分中文站点 otherwise produce unreadable text.
  - TechCrunch pages often expose useful Schema.org/meta description text even when the page is heavy; parse HTML with BeautifulSoup and inspect title, meta description, and surrounding snippets for `led by`, `valuation`, `founder`, etc. If a TechCrunch/RSS-discovered URL returns `Page not found` but the page body/sidebar still shows the headline, do **not** treat it as verified; rediscover the exact article URL or use another reputable source.
  - Google News RSS can surface aggregator mirrors, future/old recycled items, near-miss URLs, and stale press releases that match keywords but are outside the requested window. After discovery, verify the date inside the article/press-release body (`News provided by ... Jan 13, 2026`, page heading timestamp, etc.), not just the RSS pubDate or search result snippet. Drop stale resurfaced items even if the headline looks relevant. In the final assembly pass, re-check every candidate against the live cutoff computed from `date`; subagent outputs and RSS `pubDate` can include old rounds resurfaced by MSN/Sina/Google News. Do not promote those to main bullets even if the secondary article appears inside the window.
  - Run exact-title DuckDuckGo HTML queries and prefer the company/newsroom URL when available (e.g. company `/news`, `/blog`, `/insights`, `/press-releases`) over Yahoo/MSN/aggregator mirrors. Official company pages often provide founder, total funding, investor list, and product framing in one parseable page. When Business Wire pages are hard to discover or blocked, Yahoo Finance often mirrors the full Business Wire release with the same title, timestamp, investor list, and body; acceptable as near-official verification if the byline clearly says Business Wire.
  - If Google News RSS only returns a `news.google.com/rss/articles/...` wrapper, resolve it with `browser_navigate` and then inspect `location.href` plus `document.documentElement.innerText`; browser navigation often lands on the original article URL even when `requests` stays on the Google wrapper. This is especially useful for Chinese Tencent/36氪/创业邦 mirrors and for blocked/redirect-heavy business sites. Preserve the **full** Google News article ID from RSS; shortened/truncated wrapper URLs can return Google 400 even though the full wrapper resolves correctly.
  - Business Wire/GlobeNewswire releases may be mirrored on Yahoo Finance, Business Insider/Markets Insider, FinancialContent vertical sites, AFP pages, or industry sites. These mirrors are acceptable near-official verification when the byline/source clearly says Business Wire/GlobeNewswire and the body preserves timestamp, investors, founders, and release text. Prefer the real BusinessWire/GlobeNewswire URL when available, but do not spend excessive time fighting blocks if a faithful mirror plus another reputable source exists.
  - When exact-title search misses an official company post, check the company's `/sitemap.xml` and scan `<loc>` entries for `series`, `funding`, `press-release`, `newsroom`, or amount strings. Many startup sites expose newly published funding posts there before generic search indexes them.
  - When the official page is blocked but an investor page is available (e.g. fund newsroom), use the investor page as near-first-hand verification. If both are blocked, require two independent reputable reports before promoting above Medium.
- For Chinese items, Google News RSS (`hl=zh-CN&gl=CN&ceid=CN:zh-Hans`) is good for discovery. If direct search is weak, use 360/Sogou result pages to find candidate titles and publisher names, but treat them as discovery only. Prefer original/near-original pages from 科创板日报/财联社, 36氪, 投资界, 上观, 澎湃, company WeChat/public announcements; Tencent News mirrors can be acceptable when they clearly identify the original source and full article text. Sina/东方财富/经济观察网 mirrors can be useful cross-checks when they preserve the original source (e.g. 投资界/第一财经) and include full financing details.
- For Chinese robotics/具身智能 rounds with large amounts but undisclosed investor names (e.g. “多家产业巨头及一线机构”), cap confidence at Medium unless a company/investor announcement confirms the investor list. Large amount alone is not enough for High.
- If delegated subagents report they have no live web access, do not stop; run RSS/search retrieval directly with terminal/browser in the main session.
- Use RSS/search pages for discovery, not final authority. Promote candidates only after finding a first-hand announcement or at least two reputable independent sources. Keep Reuters/WSJ/Bloomberg/The Information sourced but still label anonymous-source financing talks as待确认 when no company/investor confirmation exists.

2. Deduplication
Group same company/round, remove old recycled stories.

3. Verification
Find first-hand or second independent source. Label confidence.

4. Relevance filter
Keep AI-core events. Drop generic SaaS/consumer/crypto unless AI is central.

5. Synthesis
Write date-led bullets in the user’s concise style.

6. Quality check
Check no invented details, no duplicate rounds, dates are clear, confidence is labeled.

## Quality gates

Before finalizing, verify:
- Every bullet has a date or announcement date.
- Every amount/stage/investor claim is sourced or marked undisclosed/uncertain.
- China and global sections are separated unless one side has no confirmed items.
- Low-confidence items are not mixed into high-confidence bullets.
- No markdown table unless user asks; Telegram readability is better with bullets.
- No fake precision. If exact amount is undisclosed, say undisclosed.

## When to schedule

If the user asks for a daily recurring brief, use cron with a self-contained prompt that includes:
- time window,
- source priority,
- output format,
- confidence labeling,
- delivery destination.

The cron prompt must not rely on current chat context.

For the user's recurring AI investment briefing, do not rely on `web`/`search` alone. Bind this skill to the cron job and enable fallback-capable toolsets such as `terminal`, `browser`, `web`, `search`, `file`, and `code_execution`, so the workflow can use RSS/search-page scripts and browser resolution even when configured web backends are unavailable. See `references/cron-deployment.md` for the deployment/recovery checklist.

When merging the AI investment brief with the AI industry brief, do not simply concatenate prompts. Use a combined editor/orchestrator cron with separate RSS probe modules for `ai_news` and `ai_investment`, then synthesize cross-signals after both sections are independently verified. See `references/combined-ai-daily-briefing.md` for the recommended combined cron structure, output shape, and replication handoff checklist.

## Memory/skill improvement

If the user corrects source preferences, formatting, geography, sectors, or confidence policy, save the durable preference or patch this skill. Do not save individual daily news items as memory.
