---
name: ai-news-briefing
description: AI行业简报技能 — 帮the user追踪AI行业商业动态。当用户要求"追踪AI行业新闻"、"发AI简报"、"行业动态"或cronjob触发时使用此技能。核心要求：每条新闻必须溯源核查，不可无来源直接编造。
version: 1.1
---

# AI行业简报技能

帮 the user 追踪 AI 行业的商业动态，每日定时发送简报到 Telegram。

补发/防卡死的 RSS 抓取细节见 `references/rss-catchup-playbook.md`。

the user's  `AI行业简报` cron job（<job_id>）已挂载 `~/.hermes/scripts/ai_news_rss_probe.py` 作为受控预抓取脚本；它用严格 timeout 抓取高质量 RSS / Google News 候选，避免 cron agent 在 terminal 抓取阶段 idle timeout。不要改回长时间 terminal 抓取，也不要使用 `curl | python` / pipe-to-interpreter 模式。

如果用户想把 AI 行业简报与 AI 投融资简报合并，不要简单拼接两个 prompt。保留 `ai_news` 与 `ai_investment` 两个独立 RSS probe 模块，再由一个总编排 cron 做核查、去重和交叉信号解读；合并版更适合 email 交付，Telegram 只适合测试或短通知。详细结构见 `ai-investment-briefing-workflow` 的 `references/combined-ai-daily-briefing.md`。

Follow Builders 可作为 AI builder 信号源参考，但不能替代新闻核查流程；评估细节见 `references/follow-builders-source-assessment.md`。

## 核心原则

**信息质量优先于稳定性、速度和数量。稳定性优化只能减少卡死和无效重试，不能降低来源质量、核查强度或相关性。**

**真实性优先于速度。宁可少发一条新闻，也绝不能发假新闻。**

每一条新闻都必须经过溯源核查，验证流程不可跳过。

## 工作流程

### 第一步：搜索新闻（优先轻量 RSS / HTTP，不要先开浏览器）

从以下来源搜索今日（尽量今日，最新1-2天；补发时按用户指定窗口，例如最近3天）AI行业新闻：

- 英文优先 RSS：
  - TechCrunch AI: `https://techcrunch.com/category/artificial-intelligence/feed/`
  - The Verge AI: `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
  - TechCrunch 全站: `https://techcrunch.com/feed/`
  - VentureBeat AI 备用：`https://venturebeat.com/category/ai/feed`（注意旧地址 `/ai/feed/` 会 308/404，避免反复试）
- 英文搜索备用：Google News RSS，查询 OpenAI / Anthropic / Google DeepMind / Meta AI / Nvidia / AI funding / China AI startup 等。
- 中文：36kr(36氪)、机器之心、虎嗅；可先用 Google News RSS 定位，再打开原文核查。
- X/Twitter：仅作为线索，不作为未核查来源。

**防卡死规则：**
- 每个 RSS/搜索源最多抓取 15 条。
- 单个请求设置明确 timeout；403/404/超时直接跳过，不要反复重试。
- 优先 `terminal`/轻量 HTTP 解析标题、日期、链接、description；只有需要解析 Google News 跳转或页面元信息时才用 browser。
- 不要使用 `curl | python` 这类会触发安全审批/阻塞的命令，改为 Python 内部 HTTP 请求或先保存再解析。

**搜索Query格式**：
- 英文：`OpenAI Anthropic Google DeepMind AI funding product regulation when:3d`
- 中文：`site:36kr.com AI 融资 2026 when:3d`
- 突发：`AI startup funding May 2026 when:3d`
- TML：`Thinking Machines Lab Mira Murati when:7d`

### 第二步：溯源核查（关键步骤，对每一条新闻都要做）

对于搜索结果中的每一条新闻，执行以下核查：

1. **点击新闻链接**，确认文章真实存在
2. **读取文章内容**，确认关键事实（标题、公司、金额、日期）匹配
3. **拒绝猜测**：如果链接打不开、或搜索结果里找不到原文、或关键信息对不上，**直接丢弃这条新闻**，不要凑合编一个

**核查不通过的表现**：
- 链接是 404/错误页
- 标题和内容对不上
- 公司名、人名、日期有明显出入
- 整个新闻条目搜不到原始来源

**如果所有备选新闻都核查失败**：只发核查通过的那几条，哪怕只有1条也行，不要为了凑数发未经核实的。

### 第三步：整理简报

通过核查的新闻，整理成以下格式：

```
📰 AI 行业简报 | [日期或日期范围]

## 🔴 大公司动态
- [时间] 事件标题 — 解释这句话：什么人、做了什么事、为什么重要，2-3句话。
  🔗 [原文链接]
```

分类 emoji：
- 🔴 大公司动态
- 🟠 人物动向
- 💰 资本并购
- 🌏 中美博弈 / 中国动态
- 🏛️ 政策监管
- 👷 劳动力与产业影响
- 🔥 热点事件

**补发/追赶简报：**
- 用户说“几天没跑了”“补三天量”时，日期范围写清楚，例如 `5/1–5/4 三天量`。
- 条数可以比日更更多，但仍要精选；通常 10–14 条以内。
- 按板块聚合，不要按来源流水账。
- 明确丢弃无法核查的来源，不要为了凑满三天而编。

### 第四步：交付方式

- 如果是 cronjob / scheduled task 触发：**不要调用 `send_message`**，只把简报作为 final response 输出；系统会自动投递。
- 如果是用户在普通对话里明确要求“发到 Telegram”：可使用 `send_message` 发送到 `telegram`（即用户自己的对话/home）。
- 如果只是用户询问或预览：直接在当前对话输出，不额外发送。

## 兴趣领域（按优先级）

1. AI 公司融资、并购、上市
2. AI 产品发布和技术突破
3. AI 政策监管动态
4. 中国AI创业生态
5. AI 对劳动力市场的影响

## 重点关注公司

以下公司的新闻优先跟进，**若无更新则不提**：
- OpenAI
- Anthropic
- Google DeepMind
- xAI
- Mistral AI
- Cerebras
- Meta AI
- **Thinking Machines Lab (TML)** — Mira Murati 创立的 AI 创业公司，2025年2月成立，估值$12B
- 其他 LoRA 3 大模型公司

## 核查失败的处理

如果某条新闻核查失败（如链接打不开、信息不匹配）：
- 直接丢弃，不要放进去
- 在最终简报末尾加一行：「*注：部分备选新闻经核查来源存疑，已丢弃，以可信来源为准*」

## 溯源示例

**好的处理：**
```
✅ 核查通过：Mistral AI 5亿欧元D轮融资
   - 原文链接可访问
   - 内容匹配：General Catalyst领投，估值60亿欧元
```

**坏的处理（绝对禁止）：**
```
❌ 未核查直接编造：Meta CEO黄仁勋宣布...
   （黄仁勋是NVIDIA CEO，不是Meta CEO）
   → 这条直接丢弃，不发
```
