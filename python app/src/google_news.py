import feedparser
import re

def get_top_google_news(limit=10):
    """
    Fetches the latest top news headlines and their URLs from Google News RSS.
    """
    rss_url = "https://news.google.com/rss"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:limit]:
        # Clean title (Google News titles often end with '- Source name')
        title = entry.title
        title = re.sub(r' - [^-]+$', '', title).strip()
        
        news_items.append({
            "title": title,
            "link": entry.link,
            "published": entry.published,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News"
        })
        
    return news_items

if __name__ == "__main__":
    # Test it
    results = get_top_google_news(3)
    for res in results:
        print(f"[{res['source']}] {res['title']}")
