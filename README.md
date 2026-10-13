# content-gap-audit

A Claude skill that reads a company's sitemap and shows which kinds of content types they publish too much of, and which kinds they barely touch.

It's built for IT services, consultancies and SaaS companies that compete on AI and data content marketing.

## Why this exists

Everyone in AI services says they do "thought leadership." But if you actually sort what they publish, most of it is the same kind of post: "AI for [industry]", "How we [did outcome] with AI". In other words, showcase content for buyers who already get AI.

What's missing is content for the much bigger group of people who are still asking *"what is this, and does it even apply to us?"*

This skill finds that gap with real numbers, straight from a competitor's sitemap, in a few minutes, without anyone having to read hundreds of articles by hand.

## How it was built

It came out of a real competitor audit across six companies:

- Kanerika
- KPI Partners
- Kyndryl
- Veeam
- Globant
- Muoro

Their sitemaps were pulled, the content URLs extracted, and every AI-related piece sorted into stages of the buyer journey. Mistakes made along the way, such as counting press releases and product docs as "content", were written back into the skill as rules so they don't happen again.

## The main finding

Across every audit run so far, the same pattern shows up:

> **Capability / showcase content makes up roughly 70–90% of each company's content pillars. AI Literacy, AI Readiness and Data Readiness sit at or near zero.**

Vendors are writing for buyers who are already comparing options. Almost nobody is writing for buyers who are still figuring out whether AI is for them, and that's the white space.

The skill doesn't assume this pattern will repeat. It checks for it every time.

## The 8 content pillars

Every AI-related URL gets sorted into one of these:

| # | Pillar | What it means |
|---|---|---|
| 1 | **Capability / Showcase** | "AI for [industry]" style posts. This is the leftover bucket for anything that doesn't match a clear stage. |
| 2 | **AI Literacy** | Plain-language "what is / why does it matter" explainers |
| 3 | **Tool Comparisons** | "X vs Y" posts. These look like literacy but assume the reader already knows the basics, so they're kept separate. |
| 4 | **AI Readiness** | "Is your company ready for AI?" content and assessments |
| 5 | **Data Readiness** | Data governance, quality, lineage, pipelines, modernization, but only when tied to AI |
| 6 | **AI Adoption / Maturity** | Adoption stages, maturity models |
| 7 | **Implementation / How-To** | Deploy, integrate, build, migrate |
| 8 | **Execution / ROI** | Case studies, results, ROI, transformation stories |

**Scope rule:** only AI-relevant content counts. A pure data-engineering post with no AI angle is left out. The audit is framed around "data-first AI in production", not general data content.

## How it works

```
sitemap CSV  ->  extract_content_urls.py  ->  YOU REVIEW what gets excluded
             ->  classify_pillars.py      ->  build_chart_widget.py  ->  chart
```

1. **Get the sitemap.** A CSV export works best. A live `sitemap.xml` works too.
2. **Pull out content URLs.** `extract_content_urls.py` grabs anything that looks like blog, insights, case studies, news and so on. It catches too much on purpose.
3. **Review exclusions. This step is never skipped.** Large buckets get sampled, and you see exactly what would be removed and why before anything gets dropped. Approval for one company doesn't carry over to the next.
4. **Sort into pillars.** `classify_pillars.py` reads each URL slug and assigns a pillar. You get the counts, plus a per-URL file for spot-checking.
5. **Present the gap:** what's crowded vs what's empty.
6. **Chart it.** `build_chart_widget.py` makes side-by-side bar charts, one per company, with the exact number on every bar so screenshots still make sense. Your own company goes first and gets highlighted.

## Traps found during the research

These were real mistakes from the first audit. They're now baked into [`references/noise_patterns.md`](content-gap-audit/references/noise_patterns.md):

- **Press releases pretending to be content.** Globant's whole `/news/` section (2,283 URLs) was funding announcements and award PR, and Kyndryl's (1,109) was similar. Kyndryl's real editorial content was hiding at `/perspectives/articles/`.
- **Support docs.** Veeam's `/kb1234` URLs are product help pages, not marketing.
- **Translated duplicates.** `/es/`, `/pt-br/`, `/fr/` copies can inflate counts.
- **Index pages.** A bare `/blog/` is a listing page, not an article.
- **Ugly but real URLs.** KPI Partners' old `/bid/12345/` links are real articles from a legacy CMS, so don't drop them for looking weird.
- **The Data Readiness pattern started too narrow** and under-counted data-first companies. It was broadened to cover governance, observability, lineage and similar topics.

## Why it's different

- **It uses real data, not opinion.** Counts come from the sitemap, not from someone eyeballing a blog page.
- **A human checks the exclusions.** Nothing gets dropped without you seeing it first. That's where most of the real errors in the first audit happened.
- **It's honest about its limits.** It classifies from the URL slug, not the full article text. That's good for spotting patterns (a pillar near zero across every company is a solid finding) but not for defending an exact count to a skeptical stakeholder. The skill always says this.
- **The leftover bucket isn't oversold.** "Capability / showcase" is everything that didn't match a named pillar, and it's presented that way rather than as a confident label.
- **It's built for comparison.** It runs several companies side by side, so the gap is visible at a glance.

## What's inside

```
content-gap-audit/
  SKILL.md                          # workflow and rules Claude follows
  references/noise_patterns.md      # known traps to check before classifying
  scripts/extract_content_urls.py   # step 1: sitemap -> content URLs
  scripts/classify_pillars.py       # step 2: URLs -> 8 pillars
  scripts/build_chart_widget.py     # step 3: pillar counts -> chart
```

The scripts only need Python 3, with no extra packages.

## Install

**Claude Code:** copy the `content-gap-audit` folder into `~/.claude/skills/`.

```bash
git clone https://github.com/siddheshpatankar786-commits/content-gap-audit.git
cp -r content-gap-audit/content-gap-audit ~/.claude/skills/
```

**claude.ai:** zip the `content-gap-audit` folder and upload it under Settings > Capabilities > Skills.

## How to use it

Give Claude a sitemap and ask something like:

- "audit this sitemap for content gaps"
- "compare our content to these 3 competitors"
- "where is their content weak?"

Attaching sitemap CSVs works best. You can also just name the companies.
