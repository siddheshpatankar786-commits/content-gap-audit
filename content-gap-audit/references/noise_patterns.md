# Known Noise Patterns — Check Before Classifying

These are real traps hit during the first audit (Kanerika, KPI Partners,
Kyndryl, Veeam, Globant, Muoro). A pattern matching "content-type URL"
does NOT mean it's real marketing/editorial content. Always sample
5-15 URLs from any bucket over ~50 URLs before trusting it.

## Traps seen so far

**Press release / news archives (Globant, Kyndryl)**
URLs matching `/news/` are often corporate press releases — funding
rounds, executive appointments, award announcements — not
thought-leadership content. Globant's entire "news" bucket (2,283 URLs)
was this. Kyndryl's was similar (1,109 URLs), though Kyndryl separately
has a genuine `/perspectives/articles/` section that IS real editorial
content. Always sample titles/slugs before including a "news" bucket.

**Product KB / support docs (Veeam)**
URLs matching `/kb\d+` or similar are product documentation, not
marketing content. Exclude these entirely — they answer "how do I use
feature X" for existing customers, not "why should I care about AI."

**Localized/duplicate content (Globant)**
Sitemaps with `/es/`, `/pt-br/`, `/fr/` etc. path segments may contain
the same content in multiple languages, or region-specific content
unrelated to the target market. Check whether duplicates should be
deduped or excluded based on the target market for the audit.

**Index/listing pages**
URLs like `/blog/`, `/blogs/`, `/case-studies/` with nothing after the
trailing slash are category index pages, not individual articles.
Drop these.

**Slug inconsistency across platforms**
Different CMSs use different plural/singular conventions:
- `/blog/` vs `/blogs/` (both seen — check both before concluding a
  company "has no blog")
- `/case-stud` catches both `/case-study/` and `/case-studies/`
- Old CMS migration artifacts: KPI Partners used `/bid/12345/` tracking
  IDs from a legacy platform (likely HubSpot) — these are still real
  articles, just with ugly URLs. Don't exclude on URL ugliness alone.

## Process
1. Run `extract_content_urls.py` — this over-includes by design.
2. Look at `path_breakdown` in the output. Any bucket over ~50 is worth
   sampling.
3. For each large bucket, pull 10-15 sample URLs and eyeball the slugs.
   Ask: is this a press release, product doc, or real editorial content?
4. **Confirm exclusions with the user before proceeding** — do not
   silently drop a bucket. Show what you're excluding and why, and wait
   for confirmation. (This is a hard requirement, not a suggestion —
   the user has explicitly asked to review every exclusion.)
5. Only after confirmed exclusions, proceed to classify_pillars.py.
