import os
import subprocess
import sys

def main():
    print("\n" + "="*60)
    print("🛡️  AI FAKE NEWS DETECTION SYSTEM - INTEGRITY CHECK")
    print("="*60 + "\n")
    
    # 1. Check for data
    if not os.path.exists('data/news.csv'):
        print("❌ Dataset not found (data/news.csv).")
        print("   Please ensure you have a CSV file with 'title', 'text', and 'label' columns.")
        return

    # 2. Check for models
    if not os.path.exists('models/model.pkl'):
        print("⚠️  Baseline model files not found. Initializing training...")
        try:
            # Ensure we can import src
            root_path = os.path.dirname(os.path.abspath(__file__))
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            subprocess.run([sys.executable, 'src/train_model.py'], check=True)
            print("✅ Baseline model trained and saved successfully.")
        except Exception as e:
            print(f"❌ Error during training: {e}")
    else:
        print("✅ Baseline models located (models/model.pkl)")

    # 3. Check for BERT (Optional/Heavy)
    if not os.path.exists('models/bert_model.pth'):
        print("ℹ️  BERT fine-tuned weights not found. System will use pre-trained BERT + Baseline Hybrid.")
    
    # 4. Instructions
    print("\n" + "-"*60)
    print("🚀 SYSTEM READY. CHOOSE YOUR FLAVOR:")
    print("-"*60)
    
    print("\n[OPTION 1] PREMIUM WEB DASHBOARD (Recommended)")
    print("   ↳ Command: python web_server.py")
    print("   ↳ Features: Modern UI, Glassmorphism, Google News Live, OTP Auth")
    
    print("\n[OPTION 2] STREAMLIT ANALYTICS APP")
    print("   ↳ Command: streamlit run app/streamlit_app.py")
    print("   ↳ Features: Fast prototyping, simple charts")
    
    print("\n" + "="*60)
    print("Tip: Port 8000 must be free to run the Premium Dashboard.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
