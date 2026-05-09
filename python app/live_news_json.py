import json
from src.predict import Predictor
from src.google_news import get_top_google_news
import random

def main():
    predictor = Predictor(mode='bert')
    
    # Fetch real news from Google
    news_items = get_top_google_news(limit=5)
    
    if not news_items:
        output = {"error": "Could not fetch news from Google."}
    else:
        # Add an intentionally "fake" headline
        fake_headline = {
            "title": "ALIENS INVADE NEW YORK! SHOCKING FOOTAGE UNCOVERED BY ANONYMOUS SOURCE! BREAKING: SPACE INVADERS ARE HERE TO STEAL OUR SECRETS! MIRACLE SURVIVAL REPORTED!",
            "source": "Conspiracy Daily",
            "published": "Just Now",
            "link": "#"
        }
        news_items.insert(random.randint(0, len(news_items)), fake_headline)
        
        results = []
        for news in news_items:
            prediction = predictor.predict(news['title'])
            results.append({
                "source": news.get('source', 'Unknown'),
                "title": news['title'],
                "prediction": prediction
            })
        output = {"live_news_analysis": results}
    
    with open('live_news_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
