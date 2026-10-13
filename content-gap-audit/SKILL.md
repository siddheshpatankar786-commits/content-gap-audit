---
name: content-gap-audit
description: >
  Audits a company's published content against an 8-pillar taxonomy
  (Capability/Showcase, AI Literacy, Tool Comparisons, AI Readiness, Data
  Readiness, AI Adoption/Maturity, Implementation, Execution/ROI) using its
  sitemap. Reveals over-served pillars (usually Capability/Showcase,
  Implementation) versus nearly-untouched ones (usually AI Literacy, AI
  Readiness, Data Readiness). Use whenever the user wants to analyze a
  competitor's or client's content strategy from a sitemap/URL list, find
  content gaps versus industry leaders, compare pillar distribution across
  companies, or audit an IT services/consultancy/SaaS company's
  thought-leadership output for SEO or content strategy. Trigger even
  without the phrase "content gap audit" — e.g. "check where their content
  is missing," "compare their content to competitors," "where are they weak
  content-wise," or a sitemap CSV/XML handed over with a content-strategy
  request.
---

# Content Gap Audit

Analyzes a company's published content (via sitemap) against an 8-pillar
taxonomy to reveal which content stages are oversaturated versus
untouched — built specifically for IT services / consultancy / SaaS
companies competing in AI and data-adjacent content marketing.

## The core finding this consistently surfaces

Across every audit run so far, the same pattern holds: **"Capability /
showcase" content (industry- and outcome-specific case-study-style
titles: "AI for [industry]," "[Verb-ing] [outcome] with AI") dominates
every competitor's output — typically 70-90% of their AI-relevant
content — while AI Literacy, AI Readiness, and Data Readiness sit at
or near zero.** This isn't guaranteed to repeat for every company, but
it's the pattern to specifically check for, because it's the actionable
white space: vendors are publishing for buyers who already understand
AI and are evaluating capability, not for the (likely larger) audience
still trying to understand whether/how AI applies to them at all.

## The 8-Pillar Taxonomy

1. **Capability / Showcase** — industry- or outcome-specific case-study
   titles with no explicit stage-signal keyword (the implicit/remainder
   bucket — see classify_pillars.py)
2. **AI Literacy** — plain-language "what is/why does X matter"
   explainers for a genuinely unfamiliar reader
3. **Tool/Vendor Comparisons** — "X vs Y" content (NOTE: this is
   adjacent to but distinct from true literacy — comparison content
   assumes the reader already has baseline vocabulary; don't conflate
   the two when presenting findings)
4. **AI Readiness** — "is your org ready for AI" / readiness
   assessments
5. **Data Readiness** — data governance, quality, observability,
   reliability, lineage, modernization — but ONLY when the piece is
   also AI-relevant (see Scope Rule below)
6. **AI Adoption / Maturity** — adoption-stage and maturity-model
   content
7. **Implementation / How-To** — deployment, integration, workflow,
   build guides
8. **Execution / ROI / Outcomes** — case studies, results, ROI,
   transformation stories

### Scope rule (confirm with user if unstated)

By default, this skill counts a piece toward ANY pillar (including
Data Readiness) only if it is AI-relevant per the AI_RELEVANT filter
in classify_pillars.py. Pure data-engineering content with no AI
angle is excluded — this reflects a "data-first AI in production"
framing, not a general data-content audit. If the user's positioning
is more general-data-focused, ask before broadening scope; don't
assume.

## Workflow

### Step 1: Get the sitemap(s)
Ask for a sitemap CSV (columns: Sitemap, URL) or XML export per
company being audited. If the user names a company but doesn't
provide a file, you can fetch their live sitemap.xml via web_fetch,
but a provided CSV export is more reliable (XML sitemaps sometimes
paginate or require crawling multiple index files).

### Step 2: Extract content-type URLs
Run `scripts/extract_content_urls.py <csv> <company_name>` for each
company. This over-includes by design — it's a first pass.

### Step 3: Review and confirm exclusions — DO NOT SKIP
Read `references/noise_patterns.md` for known traps. Look at the
`path_breakdown` in step 2's output — any bucket over ~50 URLs needs
sampling before you trust it. Pull 10-15 sample slugs from large
buckets and show them to the user.

**This skill's user has explicitly required confirming exclusions
before applying them, every time — do not silently drop a bucket
(press releases, KB docs, etc.) even if it matches a known noise
pattern from a prior audit. Show what you'd exclude and why, and wait
for the user's go-ahead before proceeding to Step 4.** This applies
per-company, per-audit — prior confirmations don't carry over to a
new company's sitemap, since a "news" bucket for one company might be
genuine thought-leadership for another (e.g. Kyndryl's real editorial
content lived at `/perspectives/articles/`, not `/news/`).

Build the confirmed URL list as a plain JSON list and save it (e.g.
`/tmp/<company>_confirmed.json`) for Step 4.

### Step 4: Classify into pillars
Run `scripts/classify_pillars.py <confirmed_urls.json> <company_name>`
for each company. This produces `/tmp/<company>_pillars.json` (counts)
and `/tmp/<company>_pillar_detail.json` (per-URL assignments, useful
for spot-checking or pulling example titles).

Sanity-check: if "Capability/showcase" is under ~50% for a company
that clearly does a lot of case-study marketing, or if a pillar count
looks surprising, sample `_pillar_detail.json` for that pillar before
presenting the number — a regex heuristic can misfire, and the fix is
usually a one-line pattern adjustment, not accepting a wrong number.

### Step 5: Present findings
Default framing: what's crowded (Capability/showcase, often
Implementation) vs. what's nearly empty (Literacy, Readiness,
Adoption) — this is the "gap" the user leverages for content strategy.

Always disclose: this is slug-level classification (URL text only,
not full article bodies), so it has a real ceiling — good for spotting
*patterns* (a pillar being near-zero across every company is a robust
finding) but not for defending an exact count down to the single
digit in front of a skeptical stakeholder.

### Step 6: Visualize (if requested)
Call `visualize:read_me` with `modules=["chart","interactive"]`
first, then run `scripts/build_chart_widget.py <pillars1.json>
<pillars2.json> ...` (pass the user's own company first if comparing
against competitors — it gets the highlighted/accent-border panel).
Pass the script's stdout directly as `widget_code` to
`visualize:show_widget`. This produces small-multiples bar panels,
one per company, all 8 pillars, with exact counts labeled on every
bar (labels included by default — this was a hard requirement from
the first audit, since charts often get exported/screenshotted where
interactivity is lost).

If the user wants a static export instead of (or in addition to) the
interactive widget, generate a matplotlib PNG with the same data —
ask which they need, or default to interactive-first per the
established preference, then offer static as a follow-up.

## What NOT to do

- Don't silently expand the AI-relevance filter to sweep in general
  data/tech content just because a company's total content count
  looks thin — confirm scope changes with the user first (see Scope
  rule above).
- Don't present "Capability/showcase (remainder)" as if it were a
  matched, positive category — it's everything that didn't match a
  named pillar, which includes both true capability-showcase content
  and some genuine classification misses. Frame it as "content that
  isn't literacy, readiness, adoption, or explicitly-framed
  execution" rather than implying high confidence in the label.
- Don't skip the noise-review step (Step 3) even under time pressure
  — this is where the real errors happen (see noise_patterns.md,
  written from three actual mistakes in the first audit: Globant
  press releases, Veeam KB docs, and an initially-too-narrow data
  readiness pattern that under-counted data-first positioning).
