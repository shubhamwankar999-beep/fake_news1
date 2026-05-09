from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import sys

if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8') # type: ignore
    except:
        pass

# Ensure the root directory is in sys.path so 'src' is importable
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

print("Importing Predictor...")
try:
    from src.predict import Predictor
except ImportError:
    from predict import Predictor

print("Importing Google News...")
try:
    from src.google_news import get_top_google_news
except ImportError:
    from google_news import get_top_google_news

print("Importing Database dependencies...")
try:
    from src.database import get_db, User
except ImportError:
    from database import get_db, User
from sqlalchemy.orm import Session
from fastapi import Depends
import random
from datetime import datetime, timedelta
import socket

print("Initializing FastAPI App...")
app = FastAPI(title="Fake News Guard API")

def find_free_port(start_port=8000):
    port = start_port
    while port < 9000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Set SO_REUSEADDR to avoid TIME_WAIT issues
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1
    return start_port

# --- Auth Data Models ---
class SignupRequest(BaseModel):
    email: str
    full_name: str

class OTPRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    otp: str

# 1. Signup Route
@app.post("/auth/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered. Please login.")
    
    new_user = User(email=request.email, full_name=request.full_name)
    db.add(new_user)
    db.commit()
    return {"message": "Success! You can now request an OTP to log in."}

# 2. Request OTP Route (Simulated Email)
@app.post("/auth/request-otp")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please sign up first.")
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    print(f"DEBUG: Generated OTP {otp} for user {user.email}")
    user.last_otp = otp # type: ignore
    
    # OTP expiration: 5 minutes as requested
    user.otp_expiry = datetime.now() + timedelta(minutes=5) # type: ignore
    db.commit()
    
    # Simulate sending Email
    print("\n" + "="*50)
    print(f"📧 [EMAIL GATEWAY] OTP FOR {request.email}: {otp}")
    print("="*50 + "\n")
    
    return {
        "message": f"OTP successfully sent to {request.email} (Simulation mode)",
        "otp": otp # Returning the OTP in the response for demo convenience
    }

# 3. Verify OTP Route
@app.post("/auth/verify-otp")
async def verify_otp(request: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    print(f"DEBUG: Verifying OTP for {request.email}. Input: {request.otp}, Stored: {user.last_otp if user else 'None'}")
    
    if not user or user.last_otp != request.otp:
        print(f"DEBUG: Verification FAILED for {request.email}")
        raise HTTPException(status_code=401, detail="Invalid OTP code.")
    
    # Check expiry
    if user.otp_expiry:
        expiry_time = user.otp_expiry if isinstance(user.otp_expiry, datetime) else datetime.fromisoformat(str(user.otp_expiry))
        if datetime.now() > expiry_time:
            raise HTTPException(status_code=401, detail="OTP has expired. Please request a new one.")
    
    user.last_otp = None # type: ignore
    db.commit()
    
    return {
        "message": "Login successful!",
        "user": {
            "name": user.full_name,
            "email": user.email
        }
    }

# --- Detection Logic ---
# Prediction Data Model
class PredictionRequest(BaseModel):
    text: str
    mode: str = "baseline"

# Live News Endpoint
@app.get("/live-news")
async def fetch_live_news():
    try:
        headlines = get_top_google_news(limit=6)
        return headlines
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return []

# Predictor instances (initialized lazily)
predictor_bert = None
predictor_baseline = None

@app.post("/predict")
async def predict(request: PredictionRequest):
    global predictor_bert, predictor_baseline
    
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        # Lazy initialization
        if request.mode == "bert":
            if predictor_bert is None:
                print("🧠 Initializing BERT Predictor...")
                predictor_bert = Predictor(mode="bert")
            result = predictor_bert.predict(request.text)
        else:
            if predictor_baseline is None:
                print("📊 Initializing Baseline Predictor...")
                predictor_baseline = Predictor(mode="baseline")
            result = predictor_baseline.predict(request.text)
        
        return {
            "label": result["label"],
            "confidence": result["confidence"],
            "real_percentage": result.get("real_percentage", 50.0),
            "fake_percentage": result.get("fake_percentage", 50.0),
            "highlights": result["highlights"],
            "mode": request.mode
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_login():
    return FileResponse('static/login.html')

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse('static/index.html')

# Direct access for root-level requests (compatibility with older frontend)
@app.get("/{filename}")
async def get_static_file(filename: str):
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Special case for logo
    if filename == "logo.png":
        if os.path.exists("app/logo.png"):
            return FileResponse('app/logo.png')
        return FileResponse('static/logo.png')
    
    raise HTTPException(status_code=404)

if __name__ == "__main__":
    target_port = find_free_port(8000)

    print("\n" + "="*60)
    print("🚀 FAKE NEWS GUARD SYSTEM STARTING")
    print(f"📍 ACCESS URL: http://127.0.0.1:{target_port}")
    print("📢 NOTE: Starting may take 30-60 seconds due to BERT loading.")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=target_port, log_level="info")
    except Exception as e:
        print(f"❌ FATAL: Server failed to start: {e}")
        import traceback
        traceback.print_exc()
