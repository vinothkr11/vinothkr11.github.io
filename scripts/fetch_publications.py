#!/usr/bin/env python3
"""
Fetch publications from PubMed for a given search term and generate
Jekyll-compatible markdown files in the _publications/ directory.

Usage:
    python scripts/fetch_publications.py

Configuration is read from _config.yml (author.pubmed URL).
"""

import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

SEARCH_TERM = "vinothkumar+rajan"
PUBLICATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_publications")


def search_pubmed(term, retmax=100):
    """Search PubMed and return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": term,
        "retmax": retmax,
        "retmode": "json",
        "sort": "date"
    })
    url = f"{PUBMED_SEARCH_URL}?{params}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return data["esearchresult"]["idlist"]


def fetch_summaries(pmids):
    """Fetch article summaries for a list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json"
    })
    url = f"{PUBMED_SUMMARY_URL}?{params}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return data["result"]


def sanitize_filename(title):
    """Create a URL-safe filename from a title."""
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    clean = re.sub(r'\s+', '-', clean.strip())
    return clean[:80]


def generate_markdown(article, pmid):
    """Generate a Jekyll markdown file for a publication."""
    title = article.get("title", "Untitled")
    # Remove trailing period from title if present
    title = title.rstrip(".")

    authors_list = article.get("authors", [])
    authors = ", ".join([a.get("name", "") for a in authors_list])

    source = article.get("source", "")
    volume = article.get("volume", "")
    issue = article.get("issue", "")
    pages = article.get("pages", "")
    pubdate = article.get("pubdate", "")
    doi = article.get("elocationid", "")

    # Parse date
    try:
        if len(pubdate) >= 7:
            date_obj = datetime.strptime(pubdate[:7], "%Y %b")
        elif len(pubdate) >= 4:
            date_obj = datetime.strptime(pubdate[:4], "%Y")
        else:
            date_obj = datetime.now()
    except ValueError:
        try:
            date_obj = datetime.strptime(pubdate.split()[0], "%Y")
        except (ValueError, IndexError):
            date_obj = datetime.now()

    date_str = date_obj.strftime("%Y-%m-%d")

    # Build venue string
    venue = source
    if volume:
        venue += f" {volume}"
    if issue:
        venue += f"({issue})"
    if pages:
        venue += f":{pages}"

    # Build citation
    citation = f'{authors}. "{title}." <i>{venue}</i> ({date_obj.year}).'

    # DOI link
    doi_clean = ""
    if doi and "doi:" in doi.lower():
        doi_clean = doi.split("doi:")[-1].strip() if "doi:" in doi.lower() else doi
    elif doi and "pii:" not in doi.lower():
        doi_clean = doi

    paperurl = f"https://doi.org/{doi_clean}" if doi_clean else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    slug = sanitize_filename(title)
    filename = f"{date_str}-{slug}.md"

    # Escape quotes in title for YAML
    safe_title = title.replace('"', '\\"')

    content = f"""---
title: "{safe_title}"
collection: publications
permalink: /publication/{date_str}-{slug}
date: {date_str}
venue: '{source}'
paperurl: '{paperurl}'
citation: '{citation}'
---
{authors}

[PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)
"""
    if doi_clean:
        content += f"[DOI](https://doi.org/{doi_clean})\n"

    return filename, content


def main():
    os.makedirs(PUBLICATIONS_DIR, exist_ok=True)

    print(f"Searching PubMed for: {SEARCH_TERM}")
    pmids = search_pubmed(SEARCH_TERM)
    print(f"Found {len(pmids)} articles")

    if not pmids:
        print("No articles found.")
        return

    # Remove existing auto-generated publications
    for f in os.listdir(PUBLICATIONS_DIR):
        if f.endswith(".md"):
            filepath = os.path.join(PUBLICATIONS_DIR, f)
            os.remove(filepath)
            print(f"  Removed old: {f}")

    summaries = fetch_summaries(pmids)

    count = 0
    for pmid in pmids:
        if pmid not in summaries:
            continue
        article = summaries[pmid]
        filename, content = generate_markdown(article, pmid)
        filepath = os.path.join(PUBLICATIONS_DIR, filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"  Created: {filename}")
        count += 1

    print(f"\nGenerated {count} publication files in {PUBLICATIONS_DIR}")


if __name__ == "__main__":
    main()
