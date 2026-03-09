import re
import json
import os
import feedparser
import requests

MEDIUM_USERNAME = "yasinatesim"
DEVTO_USERNAME  = "yasinatesim"
README_PATH     = "README.md"
MEDIUM_CACHE    = "medium_articles.json"  # Repoda saklanır, birikerek büyür

MEDIUM_START = "<!-- MEDIUM-ARTICLES:START -->"
MEDIUM_END   = "<!-- MEDIUM-ARTICLES:END -->"
DEVTO_START  = "<!-- DEVTO-ARTICLES:START -->"
DEVTO_END    = "<!-- DEVTO-ARTICLES:END -->"


def load_medium_cache():
    """Repodaki JSON cache'i yükle. Yoksa boş dict döndür."""
    if os.path.exists(MEDIUM_CACHE):
        with open(MEDIUM_CACHE, "r", encoding="utf-8") as f:
            # {url: {title, url, publication}} formatında saklanır
            return json.load(f)
    return {}


def save_medium_cache(cache):
    """Güncel cache'i JSON olarak repoya kaydet."""
    with open(MEDIUM_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def parse_publication(link):
    """Medium URL'inden publication adını çıkar."""
    subdomain_match = re.match(r"https://([^.]+)\.medium\.com/", link)
    path_match      = re.match(r"https://medium\.com/([^@/][^/]*)/", link)
    system_paths    = {"tag", "tags", "search", "topic", "topics",
                       "m", "about", "membership"}

    if subdomain_match:
        slug = subdomain_match.group(1)
        return slug.replace("-", " ").title()
    elif path_match:
        slug = path_match.group(1)
        if slug not in system_paths:
            return slug.replace("-", " ").title()
    return None


def fetch_medium_articles():
    cache = load_medium_cache()

    url  = f"https://medium.com/feed/@{MEDIUM_USERNAME}"
    feed = feedparser.parse(url)

    new_count = 0
    for entry in feed.entries:
        link = entry.link
        if link not in cache:
            cache[link] = {
                "title":       entry.title,
                "url":         link,
                "publication": parse_publication(link),
            }
            new_count += 1

    save_medium_cache(cache)
    print(f"   📦 Cache: {len(cache)} total | +{new_count} new")

    return list(cache.values())



def fetch_devto_articles():
    url = f"https://dev.to/api/articles?username={DEVTO_USERNAME}&per_page=100"
    response = requests.get(url, timeout=10)
    articles = []
    if response.status_code == 200:
        for item in response.json():
            articles.append({"title": item["title"], "url": item["url"]})
    return articles



def build_medium_rows(articles):
    if not articles:
        return "_No articles found._"
    rows = []
    for a in articles:
        pub = f" *({a['publication']})*" if a.get("publication") else ""
        rows.append(f'- [{a["title"]}]({a["url"]}){pub}')
    return "\n".join(rows)


def build_devto_rows(articles):
    if not articles:
        return "_No articles found._"
    return "\n".join(f'- [{a["title"]}]({a["url"]})' for a in articles)


def replace_section(content, start_marker, end_marker, new_body):
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{new_body}\n{end_marker}"
    return pattern.sub(replacement, content)


def main():
    print("📡 Fetching Medium articles (with cache)...")
    medium_articles = fetch_medium_articles()
    print(f"   ✅ {len(medium_articles)} total articles.")

    print("📡 Fetching dev.to articles...")
    devto_articles = fetch_devto_articles()
    print(f"   ✅ {len(devto_articles)} articles fetched.")

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, MEDIUM_START, MEDIUM_END,
                               build_medium_rows(medium_articles))
    content = replace_section(content, DEVTO_START, DEVTO_END,
                               build_devto_rows(devto_articles))

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md updated successfully!")


if __name__ == "__main__":
    main()
