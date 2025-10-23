#!/usr/bin/env python3
"""
scraper.py
Simple news headline scraper using requests + BeautifulSoup.

Usage:
    python scraper.py https://www.example.com/news output.txt

If no arguments given, it will scrape https://www.bbc.com/news and save to headlines.txt.
(You can change the default URL in the script.)

Notes & safety:
 - Check the target site's robots.txt and terms of service before scraping.
 - Use polite scraping: add headers, a small delay between requests, and don't overload the server.
"""

import sys
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Optional: check robots.txt (simple check)
def allowed_by_robots(base_url, user_agent='*', path='/'):
    import urllib.robotparser
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, path)
    except Exception:
        # If robots.txt cannot be fetched, we return True but warn the user.
        return True

def fetch_html(url, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NewsScraper/1.0; +https://example.com/bot)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_headlines(html):
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # 1) common headline tags (h1, h2, h3)
    for tag in soup.find_all(['h1','h2','h3']):
        text = tag.get_text(strip=True)
        if text and len(text) > 5:
            headlines.append(text)

    # 2) some sites use <a> with title attributes or specific classes
    for a in soup.find_all('a'):
        t = a.get('title') or a.get_text(strip=True)
        if t and len(t) > 10:
            headlines.append(t)

    # 3) fallback: page <title>
    title_tag = soup.title.string if soup.title else None
    if title_tag:
        headlines.append(title_tag.strip())

    # deduplicate while preserving order
    seen = set()
    unique = []
    for h in headlines:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique

def save_headlines(headlines, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for h in headlines:
            f.write(h + "\n")

def main():
    default_url = "https://www.bbc.com/news"
    default_out = "headlines.txt"

    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = default_url

    if len(sys.argv) >= 3:
        out_file = sys.argv[2]
    else:
        out_file = default_out

    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    print(f"Target URL: {url}")
    print("Checking robots.txt (best-effort)...")
    if not allowed_by_robots(url, user_agent="NewsScraper/1.0", path=parsed.path or "/"):
        print("Warning: robots.txt disallows scraping this path. Aborting.")
        return

    try:
        html = fetch_html(url)
    except Exception as e:
        print("Failed to fetch page:", e)
        return

    print("Parsing HTML and extracting headlines...")
    headlines = extract_headlines(html)
    if not headlines:
        print("No headlines found. Try a different site or inspect the site's HTML structure.")
        return

    save_headlines(headlines, out_file)
    print(f"Saved {len(headlines)} headlines to {out_file}")

if __name__ == "__main__":
    main()
