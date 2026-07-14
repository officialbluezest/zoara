"""
Real link reading service - no mocking.

Two tiers:
1. oEmbed - the clean, sanctioned way to pull public metadata for YouTube,
   X/Twitter, and TikTok without needing a logged-in session.
2. Generic HTML fetch + BeautifulSoup fallback for regular websites
   (competitor homepages, blog posts, landing pages).

Honesty note: Instagram does not offer a public no-auth oEmbed endpoint as
of this writing, and platforms that require login walls (private posts,
some Instagram content) cannot be reliably scraped without official API
access. In those cases this service degrades gracefully and asks the user
to paste in the caption/transcript text manually so Zoara still learns
from it.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ZoaraBot/1.0; +content-research)"}
TIMEOUT = 12

OEMBED_ENDPOINTS = {
    "youtube.com": "https://www.youtube.com/oembed?url={url}&format=json",
    "youtu.be": "https://www.youtube.com/oembed?url={url}&format=json",
    "twitter.com": "https://publish.twitter.com/oembed?url={url}",
    "x.com": "https://publish.twitter.com/oembed?url={url}",
    "tiktok.com": "https://www.tiktok.com/oembed?url={url}",
}


def _domain(url: str) -> str:
    for d in OEMBED_ENDPOINTS:
        if d in url:
            return d
    return ""


def fetch_oembed(url: str):
    domain = _domain(url)
    if not domain:
        return None
    endpoint = OEMBED_ENDPOINTS[domain].format(url=requests.utils.quote(url, safe=""))
    try:
        r = requests.get(endpoint, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        return None
    return None


def fetch_generic(url: str):
    """Fetch a normal webpage and extract title, meta description, and main text."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta_desc = ""
    tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if tag and tag.get("content"):
        meta_desc = tag["content"].strip()

    # Pull visible body text, trimmed - enough for the model to understand voice/content, not the whole DOM.
    for s in soup(["script", "style", "nav", "footer", "header"]):
        s.decompose()
    body_text = " ".join(soup.get_text(separator=" ").split())
    body_text = body_text[:6000]  # keep prompt sizes sane

    return {"title": title, "meta_description": meta_desc, "body_text": body_text}


def read_link(url: str):
    """
    Main entry point. Tries oEmbed first (clean structured data for
    YouTube/X/TikTok), falls back to generic scraping for everything else
    (competitor websites, blogs, most landing pages).
    """
    oembed = fetch_oembed(url)
    if oembed:
        return {
            "source": "oembed",
            "title": oembed.get("title", ""),
            "author": oembed.get("author_name", ""),
            "html_snippet": oembed.get("html", ""),
            "raw": oembed,
        }

    generic = fetch_generic(url)
    if "error" in generic:
        return {"source": "error", "error": generic["error"]}

    return {"source": "generic_scrape", **generic}
