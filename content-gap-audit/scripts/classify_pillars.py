#!/usr/bin/env python3
"""
Step 2 of the content-gap audit pipeline: classify content-bearing URLs
into the 8-pillar taxonomy, restricted to AI-relevant pieces.

Run this AFTER extract_content_urls.py AND after confirming exclusions
with the user (see references/noise_patterns.md).

Usage:
    python classify_pillars.py <confirmed_urls.json> [company_name]

Where confirmed_urls.json is a JSON file containing a list of URLs
(the content_urls list from step 1, with noise already removed).

Outputs /tmp/<company_name>_pillars.json with counts per pillar,
plus /tmp/<company_name>_pillar_detail.json with the actual
slug->pillar assignments for spot-checking.
"""
import json
import re
import sys

# Scope rule: content only counts if it's AI-relevant. Pure data-engineering
# content with no AI angle is excluded even under the broadened data-readiness
# pattern below — this was an explicit user decision (data-first AI in
# production, not general data content).
AI_RELEVANT = re.compile(
    r'\b(ai|artificial.intelligence|genai|gen.ai|llm|machine.learning|ml|'
    r'agent|agentic|chatgpt|gpt|copilot|automation|data.ai|nlp|predictive|'
    r'analytics|rag)\b',
    re.I
)

# The 8-pillar taxonomy. Order matters — first match wins, so more specific
# patterns should come before general ones if there's overlap.
PILLAR_PATTERNS = {
    'AI literacy (what/why explainers)': re.compile(
        r'\b(what.is|what.does|explained|introduction.to|understanding|'
        r'demystif|beginner|101|why.)\b', re.I),
    'Tool/vendor comparisons (X vs Y)': re.compile(r'\bvs\b', re.I),
    'AI readiness': re.compile(
        r'\bai.readiness|readiness.assessment|ai.foundation|'
        r'ai.digital.foundation\b', re.I),
    # Broadened per user direction: covers governance, observability,
    # reliability, lineage, pipeline, modernization — but ONLY when the
    # piece is already AI-relevant per the filter above.
    'Data readiness': re.compile(
        r'\bdata.readiness|data.governance|data.silos|data.quality|'
        r'data.foundation|data.maturity|data.observability|'
        r'data.reliability|data.lineage|data.pipeline|data.engineering|'
        r'data.modernization|data.migration|data.architecture|'
        r'data.infrastructure|data.integration|data.management\b', re.I),
    'AI adoption / maturity': re.compile(
        r'\badoption|maturity.model|maturity\b', re.I),
    'Implementation / how-to': re.compile(
        r'\bimplement|integration|how.to|deploy|build|workflow|migrate|'
        r'migration|hire\b', re.I),
    'Execution / ROI / outcomes': re.compile(
        r'\broi|case.study|success.story|results|value|'
        r'transformation.journey|scale|scaling\b', re.I),
}
# Anything AI-relevant that matches none of the above falls into this
# implicit 8th bucket — the dominant "capability/showcase" pattern
# (industry- and outcome-specific case-study-style titles with no
# explicit stage-signal keyword). This is computed as the remainder,
# not matched directly.


def slug_words(url):
    path = re.sub(r'https?://[^/]+', '', url).rstrip('/')
    seg = path.split('/')[-1]
    seg = re.sub(r'\.(html|htm|php)$', '', seg)
    # strip legacy tracking-ID prefixes like /bid/12345/
    seg = re.sub(r'^bid.\d+.', '', seg)
    return re.sub(r'[-_]', ' ', seg).lower()


def classify(words):
    for name, pattern in PILLAR_PATTERNS.items():
        if pattern.search(words):
            return name
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_pillars.py <confirmed_urls.json> [company_name]")
        sys.exit(1)

    urls_path = sys.argv[1]
    company = sys.argv[2] if len(sys.argv) > 2 else 'company'

    with open(urls_path) as f:
        data = json.load(f)
    urls = data if isinstance(data, list) else data.get('content_urls', [])

    counts = {k: 0 for k in PILLAR_PATTERNS}
    counts['Capability / showcase (remainder)'] = 0
    detail = []
    total_ai_relevant = 0

    for u in urls:
        words = slug_words(u)
        if not AI_RELEVANT.search(words):
            continue
        total_ai_relevant += 1
        pillar = classify(words)
        if pillar is None:
            pillar = 'Capability / showcase (remainder)'
        counts[pillar] += 1
        detail.append({'url': u, 'slug': words, 'pillar': pillar})

    result = {
        'company': company,
        'total_ai_relevant': total_ai_relevant,
        'pillar_counts': counts,
    }

    with open(f'/tmp/{company}_pillars.json', 'w') as f:
        json.dump(result, f, indent=2)
    with open(f'/tmp/{company}_pillar_detail.json', 'w') as f:
        json.dump(detail, f, indent=2)

    print(f"{company}: {total_ai_relevant} AI-relevant content pieces")
    for k, v in counts.items():
        pct = round(100 * v / total_ai_relevant, 1) if total_ai_relevant else 0
        print(f"  {k}: {v} ({pct}%)")
    print(f"\nSaved to /tmp/{company}_pillars.json")
    print(f"Detail (for spot-checking) saved to /tmp/{company}_pillar_detail.json")
    print("\nNOTE: This is slug-level classification, not full-article-text")
    print("classification. Always disclose this limitation when presenting")
    print("results — a 'Capability/showcase' or single-digit pillar count")
    print("can shift with better title/intro-paragraph-level classification.")


if __name__ == '__main__':
    main()
