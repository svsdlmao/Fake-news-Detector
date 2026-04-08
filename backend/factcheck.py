"""Fact-checking module: searches external fact-check databases for related claims."""
import os
import re
import requests
from urllib.parse import quote_plus

GOOGLE_FACTCHECK_API = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
GOOGLE_API_KEY = os.environ.get("GOOGLE_FACTCHECK_API_KEY", "")


def extract_key_phrases(text, max_phrases=3):
    """Extract the most important phrases from text for searching."""
    # Take first 200 chars or first 2 sentences, whichever is shorter
    sentences = re.split(r'[.!?]+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    key_phrases = []
    for s in sentences[:max_phrases]:
        # Trim to reasonable search length
        phrase = s[:150].strip()
        if phrase:
            key_phrases.append(phrase)
    if not key_phrases and text.strip():
        key_phrases.append(text[:150].strip())
    return key_phrases


def search_google_factcheck_api(query):
    """Search Google Fact Check Tools API for related claims."""
    if not GOOGLE_API_KEY:
        return []

    try:
        params = {
            "query": query,
            "key": GOOGLE_API_KEY,
            "languageCode": "en",
            "pageSize": 5,
        }
        resp = requests.get(GOOGLE_FACTCHECK_API, params=params, timeout=5)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []
        for claim in data.get("claims", []):
            claim_text = claim.get("text", "")
            for review in claim.get("claimReview", []):
                results.append({
                    "claim": claim_text,
                    "source": review.get("publisher", {}).get("name", "Unknown"),
                    "url": review.get("url", ""),
                    "rating": review.get("textualRating", "Unknown"),
                    "title": review.get("title", ""),
                })
        return results[:5]
    except Exception:
        return []


def search_factcheck_fallback(query):
    """Fallback: scrape Google search results for fact-checks from known sites."""
    fact_check_sites = "site:snopes.com OR site:politifact.com OR site:factcheck.org OR site:reuters.com/fact-check OR site:apnews.com/hub/ap-fact-check"
    search_query = quote_plus(f"{query} {fact_check_sites}")
    search_url = f"https://www.google.com/search?q={search_query}&num=5"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(search_url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for g in soup.select("div.g, div[data-sokoban-container]"):
            link_tag = g.select_one("a[href]")
            title_tag = g.select_one("h3")
            snippet_tag = g.select_one("div[data-sncf], span.st, div.VwiC3b")

            if not link_tag or not title_tag:
                continue

            url = link_tag.get("href", "")
            if not url.startswith("http"):
                continue

            # Only include results from known fact-check sites
            trusted = ["snopes.com", "politifact.com", "factcheck.org", "reuters.com", "apnews.com"]
            if not any(site in url for site in trusted):
                continue

            source = "Unknown"
            for site in trusted:
                if site in url:
                    source = site.split(".")[0].capitalize()
                    if source == "Factcheck":
                        source = "FactCheck.org"
                    break

            results.append({
                "claim": snippet_tag.get_text(strip=True) if snippet_tag else "",
                "source": source,
                "url": url,
                "rating": "",
                "title": title_tag.get_text(strip=True),
            })

        return results[:5]
    except Exception:
        return []


def find_fact_checks(text):
    """
    Search for fact-checks related to the given text.
    Returns a list of fact-check results with source, rating, url, etc.
    """
    phrases = extract_key_phrases(text)
    all_results = []
    seen_urls = set()

    for phrase in phrases:
        # Try Google Fact Check API first
        results = search_google_factcheck_api(phrase)

        # Fallback to web search if no API key or no results
        if not results:
            results = search_factcheck_fallback(phrase)

        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    return all_results[:5]
