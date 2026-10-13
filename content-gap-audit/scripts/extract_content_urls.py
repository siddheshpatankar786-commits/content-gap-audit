#!/usr/bin/env python3
"""
Step 1 of the content-gap audit pipeline: extract content-bearing URLs
from a raw sitemap CSV (columns: Sitemap, URL — or just URL).

This is a FIRST PASS only. It over-includes on purpose (press releases,
KB docs, etc. often match the content-type patterns below). The human
review step happens after this — see references/noise_patterns.md for
known traps to check for before proceeding to classification.

Usage:
    python extract_content_urls.py <sitemap.csv> [company_name]

Outputs a JSON file at /tmp/<company_name>_content_urls.json with:
    - total_urls: count of all URLs in the sitemap
    - content_urls: list of URLs matching content-type patterns
    - path_breakdown: counts by matched pattern (blog, news, kb, etc.)
      so you can eyeball which buckets are large before trusting them
"""
import csv
import json
import re
import sys
from collections import Counter

CONTENT_PATTERNS = re.compile(
    r'/(blog|blogs|insight|insights|article|articles|resource|resources|'
    r'case-stud|case-studies|perspective|perspectives|news|whitepaper|'
    r'guide|guides|kb\d|thought-leadership|success-stories)',
    re.I
)
EXCLUDE_PATTERNS = re.compile(
    r'\.(pdf|jpg|png|jpeg|css|js|xml)$|/tag/|/tags/|/category/|/page/\d|/author/|feed',
    re.I
)


def load_urls(csv_path):
    with open(csv_path, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    has_header = 'URL' in rows[0] or 'Sitemap' in rows[0]
    start = 1 if has_header else 0
    urls = [r[-1].strip() for r in rows[start:] if r and r[-1].strip()]
    return urls


def classify_path(url):
    m = CONTENT_PATTERNS.search(url)
    if not m:
        return None
    key = m.group(1).lower()
    key = re.sub(r'kb\d+', 'kb', key)
    return key


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_content_urls.py <sitemap.csv> [company_name]")
        sys.exit(1)

    csv_path = sys.argv[1]
    company = sys.argv[2] if len(sys.argv) > 2 else 'company'

    urls = load_urls(csv_path)
    content_urls = []
    path_breakdown = Counter()

    for u in urls:
        if EXCLUDE_PATTERNS.search(u):
            continue
        cat = classify_path(u)
        if cat:
            content_urls.append(u)
            path_breakdown[cat] += 1

    content_urls = list(dict.fromkeys(content_urls))  # dedupe, preserve order

    result = {
        'company': company,
        'total_urls': len(urls),
        'content_url_count': len(content_urls),
        'content_urls': content_urls,
        'path_breakdown': dict(path_breakdown.most_common()),
    }

    out_path = f'/tmp/{company}_content_urls.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"{company}: {len(urls)} total URLs -> {len(content_urls)} content-type URLs")
    print("Path breakdown (REVIEW THESE before trusting them as real content):")
    for k, v in path_breakdown.most_common():
        print(f"  {k}: {v}")
    print(f"\nSaved to {out_path}")
    print("\nNEXT STEP: Do not proceed to classification yet.")
    print("Sample the large buckets above (especially 'news', 'kb', 'resource')")
    print("to check for press releases, product docs, or other noise before")
    print("continuing. See references/noise_patterns.md for known traps.")


if __name__ == '__main__':
    main()
