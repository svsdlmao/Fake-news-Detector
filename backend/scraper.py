"""Web scraper for extracting article text from news URLs."""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_article(url: str) -> str:
    """
    Fetch and extract article text from a URL.

    Returns cleaned article text (minimum 100 characters).
    Raises ValueError if article text is too short or cannot be extracted.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out after 10 seconds")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove unwanted elements
    for tag in soup.find_all(['nav', 'footer', 'header', 'aside', 'script',
                               'style', 'iframe', 'noscript', 'form']):
        tag.decompose()

    # Try to find article content in order of specificity
    article_text = ''

    # Strategy 1: Look for <article> tag
    article = soup.find('article')
    if article:
        paragraphs = article.find_all('p')
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

    # Strategy 2: Look for common content containers
    if len(article_text) < 100:
        for selector in ['[role="main"]', '.article-body', '.story-body',
                         '.post-content', '.entry-content', '.article-content',
                         '#article-body', 'main']:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                article_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
                if len(article_text) >= 100:
                    break

    # Strategy 3: Get all paragraphs from body
    if len(article_text) < 100:
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

    # Clean up whitespace
    article_text = ' '.join(article_text.split())

    if len(article_text) < 100:
        raise ValueError("Could not extract sufficient article text from URL")

    return article_text
