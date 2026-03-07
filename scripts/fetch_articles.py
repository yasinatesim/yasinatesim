import re
import feedparser
import requests

MEDIUM_USERNAME = "yasinatesim"
DEVTO_USERNAME  = "yasinatesim"
README_PATH     = "README.md"

MEDIUM_START = "<!-- MEDIUM-ARTICLES:START -->"
MEDIUM_END   = "<!-- MEDIUM-ARTICLES:END -->"
DEVTO_START  = "<!-- DEVTO-ARTICLES:START -->"
DEVTO_END    = "<!-- DEVTO-ARTICLES:END -->"


def fetch_medium_articles():
    url  = f"https://medium.com/feed/@{MEDIUM_USERNAME}"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        publication = None
        link = entry.link

        subdomain_match = re.match(r"https://([^.]+)\.medium\.com/", link)
        path_match      = re.match(r"https://medium\.com/([^@/][^/]*)/", link)

        if subdomain_match:
            slug = subdomain_match.group(1)
            publication = slug.replace("-", " ").title()
        elif path_match:
            slug = path_match.group(1)
            system_paths = {"tag", "tags", "search", "topic", "topics", "m", "about", "membership"}
            if slug not in system_paths:
                publication = slug.replace("-", " ").title()

        articles.append({
            "title":       entry.title,
            "url":         link,
            "publication": publication,
        })
    return articles


def fetch_devto_articles():
    page, articles = 1, []
    while True:
        url      = f"https://dev.to/api/articles?username={DEVTO_USERNAME}&per_page=100&page={page}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            break
        batch = response.json()
        if not batch:
            break
        for item in batch:
            articles.append({"title": item["title"], "url": item["url"]})
        page += 1
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
    print("📡 Fetching Medium articles...")
    medium_articles = fetch_medium_articles()
    print(f"   ✅ {len(medium_articles)} articles fetched.")

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
