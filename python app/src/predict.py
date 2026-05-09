import joblib
import os
from .preprocessing import clean_text
from .bert_model import FakeNewsBERT

class Predictor:
    def __init__(self, mode='bert'):
        self.mode = mode
        # BERT takes time to load, so we initialize it when needed.
        self.model = None

    def load_model(self):
        """
        Loads the model based on self.mode.
        Persists it to self.model as either a FakeNewsBERT instance 
        or a dictionary for the baseline.
        """
        if self.mode == 'bert':
            try:
                self.model = FakeNewsBERT()
                print("✅ BERT model loaded successfully.")
            except Exception as e:
                print(f"⚠️ Error loading BERT: {e}. Falling back to baseline mode.")
                self.mode = 'baseline'
                self.load_model()
        else:
            # Baseline TF-IDF + Logistic Regression
            try:
                if not os.path.exists('models/model.pkl') or not os.path.exists('models/tfidf.pkl'):
                    print("⚠️ Baseline model files missing.")
                    self.model = None
                    return

                self.model = {
                    'clf': joblib.load('models/model.pkl'),
                    'tfidf': joblib.load('models/tfidf.pkl')
                }
                print("✅ Baseline models loaded successfully.")
            except Exception as e:
                print(f"⚠️ Warning: Error loading models: {e}. Using dummy logic.")
                self.model = None

    def predict(self, text):
        cleaned = clean_text(text)
        text_lower = text.lower()
        
        # Keywords for highlighting in UI
        fake_keywords = ["breaking", "shocking", "miracle", "exposed", "truth about", "uncovered", "conspiracy", "hidden", "secret", "vault", "aliens", "mystery", "instant", "magic", "wonder", "insane", "unbelievable", "hoax", "weight loss", "cure", "leak", "classified", "warning", "scandal", "secret code", "mysterious", "anonymous source", "unreliable"]
        real_keywords = ["reuters", "bbc", "nasa", "study", "report", "official", "confirmed", "government", "science", "journal", "university", "announced", "decided", "research", "published", "according to", "spokesman", "statement", "representative", "spokesperson", "expert", "data analysis", "verified fact"]
        
        found_fake = [word for word in fake_keywords if word in text_lower]
        found_real = [word for word in real_keywords if word in text_lower]

        # Use heuristics for baseline adjustment later
        fake_score = len(found_fake) 
        real_score = len(found_real)
        
        # Check for ALL CAPS (highly indicative of sensationalism)
        caps_words = [word for word in text.split() if len(word) > 5 and word.isupper()]
        if caps_words:
            fake_score += 1.5 
            found_fake.extend(caps_words)

        # 1. Attempt Primary Prediction (BERT)
        if self.mode == 'bert':
            try:
                if not self.model:
                    self.load_model()
                
                if isinstance(self.model, FakeNewsBERT):
                    label, confidence = self.model.predict(cleaned)
                    real_pct = float(confidence) * 100 if label == "REAL" else (1 - float(confidence)) * 100
                    fake_pct = float(confidence) * 100 if label == "FAKE" else (1 - float(confidence)) * 100
                    return {
                        "label": label,
                        "confidence": float(confidence),
                        "real_percentage": round(real_pct, 2),
                        "fake_percentage": round(fake_pct, 2),
                        "highlights": found_fake if label == "FAKE" else found_real
                    }
            except Exception as e:
                print(f"🚨 BERT Inference Failed: {e}")
                # Fall through to baseline attempt

        # 2. Baseline Model Logic (TF-IDF + LR)
        if not self.model or self.mode == 'bert': 
             if not isinstance(self.model, dict):
                 self.load_model() # Try loading baseline

        if isinstance(self.model, dict):
            try:
                clf = self.model['clf']
                tfidf = self.model['tfidf']
                
                X = tfidf.transform([cleaned])
                prediction = clf.predict(X)[0]
                
                # Dynamic initial label mapping - FIX: Ensure uppercase string labels
                label = "FAKE" if prediction == 1 else "REAL"
                
                # Calculate real confidence using predict_proba
                probs = clf.predict_proba(X)[0]
                import numpy as np
                try:
                    match = np.where(clf.classes_ == prediction)[0]
                    idx = match[0] if len(match) > 0 else np.argmax(probs)
                    confidence = float(probs[idx])
                except:
                    confidence = float(max(probs))
                
                # --- Hybrid Enhancement: Linguistic Heuristics ---
                if fake_score > real_score + 2:
                    label = "FAKE"
                    confidence = max(confidence, 0.75) 
                elif real_score > fake_score + 2:
                    label = "REAL"
                    confidence = max(confidence, 0.75)

                real_pct = float(confidence) * 100 if label == "REAL" else (1 - float(confidence)) * 100
                fake_pct = float(confidence) * 100 if label == "FAKE" else (1 - float(confidence)) * 100
                return {
                    "label": label,
                    "confidence": float(confidence),
                    "real_percentage": round(real_pct, 2),
                    "fake_percentage": round(fake_pct, 2),
                    "highlights": found_fake if label == "FAKE" else found_real
                }
            except Exception as e:
                print(f"🚨 Baseline Prediction Error: {e}")

        # 3. Last Resort: Dummy Deterministic Heuristic logic
        return self._dummy_predict(found_fake, found_real)

    def _dummy_predict(self, found_fake, found_real):
        """
        Deterministic Heuristic Scorer: Calculates a content-driven score 
        when ML models are loading or unavailable. No random values.
        """
        fake_score = len(found_fake)
        real_score = len(found_real)
        
        # Calculate a deterministic base confidence based on the strength of evidence
        total_hits = fake_score + real_score
        if total_hits > 0:
            evidence_strength = min(total_hits * 0.05, 0.35)
            base_confidence = 0.60 + evidence_strength
        else:
            base_confidence = 0.52 
            
        if fake_score > real_score:
            label = "FAKE"
            confidence = base_confidence
        elif real_score > fake_score:
            label = "REAL"
            confidence = base_confidence
        else:
            # FIX: Ensure label is REAL (uppercase) and consistent
            label = "REAL" 
            confidence = 0.50
        
        real_pct = float(confidence) * 100 if label == "REAL" else (1 - float(confidence)) * 100
        fake_pct = float(confidence) * 100 if label == "FAKE" else (1 - float(confidence)) * 100
        return {
            "label": label,
            "confidence": float(confidence),
            "real_percentage": round(real_pct, 2),
            "fake_percentage": round(fake_pct, 2),
            "highlights": found_fake if label == "FAKE" else found_real
        }

