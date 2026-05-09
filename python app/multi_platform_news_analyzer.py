import feedparser
import re
import json
import time
from src.predict import Predictor

# List of news platforms and their RSS feeds
NEWS_FEEDS = {
    "Google News": "https://news.google.com/rss",
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "CNN Top Stories": "http://rss.cnn.com/rss/cnn_topstories.rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml"
}

def clean_title(title):
    # Remove source suffix often found in Google News (e.g., " - BBC News")
    return re.sub(r' - [^-]+$', '', title).strip()

def analyze_all_platforms():
    print("🧠 Loading BERT Model...")
    predictor_bert = Predictor(mode='bert')
    print("📊 Loading Baseline Model (Old Version)...")
    predictor_baseline = Predictor(mode='baseline')
    
    all_results = []
    
    print("\n" + "="*70)
    print("📡 GLOBAL NEWS AUTHENTICITY ANALYSIS (BERT + BASELINE DUAL-MODE)")
    print("="*70)
    
    for platform, url in NEWS_FEEDS.items():
        print(f"\n📥 Fetching from {platform}...")
        try:
            feed = feedparser.parse(url)
            # Take top 3 from each platform
            for entry in feed.entries[:3]:
                title = clean_title(entry.title)
                
                # Perform predictions with both versions
                pred_bert = predictor_bert.predict(title)
                pred_base = predictor_baseline.predict(title)
                
                # Logic for "Deactivation" (Flagging) - If either flags it, mark as cautious
                status = "ACTIVE"
                if pred_bert['label'] == "FAKE" or pred_base['label'] == "FAKE":
                    if pred_bert['confidence'] > 0.7 or pred_base['confidence'] > 0.7:
                        status = "FLAGGED / DEACTIVATED"
                
                result = {
                    "platform": platform,
                    "title": title,
                    "link": entry.link,
                    "bert": {
                        "label": pred_bert['label'],
                        "confidence": f"{pred_bert['confidence']:.2%}"
                    },
                    "baseline": {
                        "label": pred_base['label'],
                        "confidence": f"{pred_base['confidence']:.2%}"
                    },
                    "status": status,
                    "highlights": list(set(pred_bert['highlights'] + pred_base['highlights']))
                }
                all_results.append(result)
                
                icon_bert = "🚨" if pred_bert['label'] == "FAKE" else "✅"
                icon_base = "🚨" if pred_base['label'] == "FAKE" else "✅"
                
                print(f"[{platform}] {title[:60]}...")
                print(f"   ↳ BERT: {icon_bert} {pred_bert['label']} ({pred_bert['confidence']:.2%})")
                print(f"   ↳ BASE: {icon_base} {pred_base['label']} ({pred_base['confidence']:.2%}) [Old Version]")
                
                if status != "ACTIVE":
                    print(f"   ⚠️ ACTION: {status}")
        except Exception as e:
            print(f"   ❌ Error fetching {platform}: {e}")
            
    # Save results to JSON
    with open('global_news_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4)
    
    print("\n" + "="*70)
    print(f"✅ Analysis complete. {len(all_results)} headlines analyzed.")
    print("Dual-mode results saved to: global_news_analysis.json")
    print("="*70)

if __name__ == "__main__":
    analyze_all_platforms()
