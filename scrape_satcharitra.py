#!/usr/bin/env python3
"""
Scrape Sri Sai Satcharitra (Telugu) chapters from funnotes.net
into a single chapters.json for the reader PWA.

Usage:
    pip install requests beautifulsoup4
    python scrape_satcharitra.py

Output:
    chapters.json  -> [{ "index": 0, "title": "...", "paragraphs": ["...", ...] }, ...]
    raw_cache/     -> cached HTML (delete to force re-download)

Be polite: the script waits 1.5s between requests and caches everything,
so the site is hit at most once per page, ever.
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

BASE = "https://www.funnotes.net/"
INDEX_URL = urljoin(BASE, "sai_satcharitra_telugu.php")
CACHE_DIR = Path("raw_cache")
OUT_FILE = Path("chapters.json")
DELAY_SECONDS = 1.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (personal devotional reader project; one-time fetch)"
}

TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")


def fetch(url: str, cache_key: str) -> str:
    """Fetch a URL with local file cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    print(f"  fetching {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    cache_file.write_text(resp.text, encoding="utf-8")
    time.sleep(DELAY_SECONDS)
    return resp.text


def get_chapter_links(index_html: str) -> list[dict]:
    """Extract chapter page links from the index, in document order."""
    soup = BeautifulSoup(index_html, "html.parser")
    links, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "TopicOfFortnight.php" not in href:
            continue
        full = urljoin(INDEX_URL, href)
        key = parse_qs(urlparse(full).query).get("tofTpcFl", [full])[0]
        if key in seen:
            continue
        seen.add(key)
        links.append({"url": full, "key": key, "link_text": a.get_text(strip=True)})
    return links


def telugu_ratio(text: str) -> float:
    if not text:
        return 0.0
    return len(TELUGU_RE.findall(text)) / len(text)


def extract_chapter(html: str) -> dict:
    """Pull title + Telugu paragraphs: flatten page text, keep Telugu lines."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    paragraphs = []
    for line in soup.get_text(separator="\n").split("\n"):
        line = line.strip()
        if len(line) < 2:
            continue
        if telugu_ratio(line) >= 0.3:
            if not paragraphs or paragraphs[-1] != line:  # drop repeats
                paragraphs.append(line)

    title = paragraphs[0] if paragraphs else ""
    return {"title": title, "paragraphs": paragraphs}


def main():
    print(f"Fetching index: {INDEX_URL}")
    index_html = fetch(INDEX_URL, "index")
    links = get_chapter_links(index_html)
    print(f"Found {len(links)} chapter links.")
    if not links:
        print("No links found — the index page structure may differ. "
              "Open raw_cache/index.html and check the <a> hrefs.")
        return

    chapters = []
    for i, link in enumerate(links):
        print(f"[{i + 1}/{len(links)}] {link['link_text'] or link['key']}")
        html = fetch(link["url"], link["key"])
        ch = extract_chapter(html)
        chapters.append({
            "index": i,
            "link_text": link["link_text"],
            "source_key": link["key"],
            "title": ch["title"],
            "paragraphs": ch["paragraphs"],
        })
        n_chars = sum(len(p) for p in ch["paragraphs"])
        print(f"    -> {len(ch['paragraphs'])} paragraphs, {n_chars} chars")
        if n_chars < 500:
            print("    !! suspiciously short — inspect this page's cached HTML")

    OUT_FILE.write_text(
        json.dumps(chapters, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    total = sum(len(p) for c in chapters for p in c["paragraphs"])
    print(f"\nWrote {OUT_FILE} — {len(chapters)} chapters, {total:,} Telugu chars total.")
    print("Spot-check chapters.json (first/middle/last chapter) before we build the app.")


if __name__ == "__main__":
    main()
