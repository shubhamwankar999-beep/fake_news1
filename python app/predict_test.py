from src.predict import Predictor
import sys

def test_prediction(news_text):
    print(f"\nAnalyzing News: \"{news_text[:100]}...\"")
    predictor = Predictor(mode='bert')
    result = predictor.predict(news_text)
    
    print("-" * 30)
    print(f"RESULT: {result['label']}")
    print(f"OVERALL CONFIDENCE: {result['confidence']:.2%}")
    if 'real_percentage' in result:
        print(f"REAL PROBABILITY: {result['real_percentage']}%")
        print(f"FAKE PROBABILITY: {result['fake_percentage']}%")
    print(f"HIGHLIGHTS FOUND: {', '.join(result['highlights']) if result['highlights'] else 'None'}")
    print("-" * 30)

if __name__ == "__main__":
    # Test 1: Real News
    real_news = "@All google real news ."
    test_prediction(real_news)
    
    # Test 2: Fake News
    fake_news = "@All google fake news detectors!"
    test_prediction(fake_news)
    
    # Allow user input
    if len(sys.argv) > 1:
        user_news = " ".join(sys.argv[1:])
        test_prediction(user_news)
