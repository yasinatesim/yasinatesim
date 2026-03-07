import re
import feedparser
import requests
from datetime import datetime

MEDIUM_USERNAME = "yasinatesim"
DEVTO_USERNAME  = "yasinatesim"
MAX_ARTICLES    = 5
README_PATH     = "README.md"

MEDIUM_START = "<!-- MEDIUM-ARTICLES:START -->"
MEDIUM_END   = "<!-- MEDIUM-ARTICLES:END -->"
DEVTO_START  = "<!-- DEVTO-ARTICLES:START -->"
DEVTO_END    = "<!-- DEVTO-ARTICLES:END -->"


def fetch_medium_articles():
    url  = f"https://medium.com/feed/@{MEDIUM_USERNAME}"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:MAX_ARTICLES]:
        date = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            date = datetime(*entry.published_parsed[:3]).strftime("%b %d, %Y")
        articles.append({"title": entry.title, "url": entry.link, "date": date})
    return articles


def fetch_devto_articles():
    url      = f"https://dev.to/api/articles?username={DEVTO_USERNAME}&per_page={MAX_ARTICLES}"
    response = requests.get(url, timeout=10)
    articles = []
    if response.status_code == 200:
        for item in response.json()[:MAX_ARTICLES]:
            date = ""
            if item.get("published_at"):
                date = datetime.fromisoformat(
                    item["published_at"].replace("Z", "+00:00")
                ).strftime("%b %d, %Y")
            articles.append({
                "title": item["title"],
                "url":   item["url"],
                "date":  date,
            })
    return articles


def build_article_rows(articles):
    if not articles:
        return "_No articles found._"
    rows = []
    for a in articles:
        date_badge = (
            f'<sub>{a["date"]}</sub> ' if a["date"] else ""
        )
        rows.append(f'- {date_badge}[{a["title"]}]({a["url"]})')
    return "\n".join(rows)


def replace_section(content, start_marker, end_marker, new_body):
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{new_body}\n{end_marker}"
    return pattern.sub(replacement, content)


def main():
    print("📡 Fetching Medium articles...")
    medium_articles = fetch_medium_articles()
    print(f"   ✅ {len(medium_articles)} articles fetched.")

    print("📡 Fetching dev.to articles...")
    devto_articles = fetch_devto_articles()
    print(f"   ✅ {len(devto_articles)} articles fetched.")

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, MEDIUM_START, MEDIUM_END,
                               build_article_rows(medium_articles))
    content = replace_section(content, DEVTO_START, DEVTO_END,
                               build_article_rows(devto_articles))

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md updated successfully!")


if __name__ == "__main__":
    main()
