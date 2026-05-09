import json
from src.predict import Predictor

def main():
    predictor = Predictor(mode='bert')
    real_news = "All google real news detectors."
    fake_news = "All google fake news detectors!"
    
    result_real = predictor.predict(real_news)
    result_fake = predictor.predict(fake_news)
    
    output = {
        "real_news": result_real,
        "fake_news": result_fake
    }
    
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
