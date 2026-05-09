import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.predict import Predictor
from src.google_news import get_top_google_news
import random

def analyze_live_news():
    print("\n" + "="*50)
    print("🌍 FETCHING LIVE NEWS FROM GOOGLE RSS")
    print("="*50)
    
    # 1. Fetch real news from Google
    news_items = get_top_google_news(limit=5)
    
    if not news_items:
        print("❌ Could not fetch news from Google.")
        return
        
    print(f"✅ Fast-fetching {len(news_items)} trending headlines...\n")
    
    # 2. Add an intentionally "fake" headline to the mix to show detection
    fake_headline = {
        "title": "BREAKING: Secret Alien Spaceship Discovered Hidden Underwater in Pacific Ocean! Miracle Cure Found Inside!",
        "source": "Conspiracy Daily",
        "published": "Just Now",
        "link": "#"
    }
    
    # Insert it randomly into the list
    news_items.insert(random.randint(0, len(news_items)), fake_headline)
    
    # 3. Model init
    predictor = Predictor(mode='bert')
    
    # 4. Predict
    print("-" * 60)
    for i, news in enumerate(news_items, 1):
        print(f"📰 NEWS #{i}")
        print(f"SOURCE : {news.get('source', 'Unknown')}")
        print(f"TITLE  : {news['title']}")
        
        result = predictor.predict(news['title'])
        label = result['label']
        conf = result['confidence']
        hi = result['highlights']
        
        icon = '✅' if label == "REAL" else '🚨'
        print(f"VERDICT: {icon} {label} ({conf:.2%} confidence)")
        if hi:
            print(f"FLAGS  : {', '.join(hi)}")
        print("-" * 60)

if __name__ == "__main__":
    analyze_live_news()
