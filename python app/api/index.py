from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys
import random
from datetime import datetime, timedelta

# Ensure the root directory (parent of api/) is in sys.path so 'src' is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.join(current_dir, "..")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Importing project logic from src/
try:
    from src.predict import Predictor
except ImportError:
    from predict import Predictor

try:
    from src.google_news import get_top_google_news
except ImportError:
    from google_news import get_top_google_news

try:
    from src.database import get_db, User
except ImportError:
    from database import get_db, User
from sqlalchemy.orm import Session

app = FastAPI(title="Fake News Guard API - Vercel")

# Mount static files relative to root
static_dir = os.path.join(root_path, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Auth Models
class SignupRequest(BaseModel):
    email: str
    full_name: str

class OTPRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    otp: str

class PredictionRequest(BaseModel):
    text: str
    mode: str = "baseline"

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

# 2. Request OTP Route
@app.post("/auth/request-otp")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please sign up first.")
    otp = str(random.randint(100000, 999999))
    user.last_otp = otp # type: ignore
    user.otp_expiry = datetime.now() + timedelta(minutes=5) # type: ignore
    db.commit()
    return {"message": "OTP successfully sent (Simulation mode)", "otp": otp}

# 3. Verify OTP Route
@app.post("/auth/verify-otp")
async def verify_otp(request: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or user.last_otp != request.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP code.")
    if user.otp_expiry:
        expiry_time = user.otp_expiry if isinstance(user.otp_expiry, datetime) else datetime.fromisoformat(str(user.otp_expiry))
        if datetime.now() > expiry_time:
            raise HTTPException(status_code=401, detail="OTP has expired.")
    user.last_otp = None # type: ignore
    db.commit()
    return {"message": "Login successful!", "user": {"name": user.full_name, "email": user.email}}

# --- Detection Logic ---
@app.get("/live-news")
async def fetch_live_news():
    try:
        return get_top_google_news(limit=6)
    except Exception:
        return []

predictor_bert = None
predictor_baseline = None

@app.post("/predict")
async def predict(request: PredictionRequest):
    global predictor_bert, predictor_baseline
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")
    try:
        if request.mode == "bert":
            if predictor_bert is None:
                predictor_bert = Predictor(mode="bert")
            result = predictor_bert.predict(request.text)
        else:
            if predictor_baseline is None:
                predictor_baseline = Predictor(mode="baseline")
            result = predictor_baseline.predict(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root & Static Routes
@app.get("/health")
async def health():
    return {"status": "ok", "message": "Fake News Guard API is running"}

@app.get("/")
@app.get("/index.html")
async def read_login():
    return FileResponse(os.path.join(static_dir, 'login.html'))

@app.get("/dashboard")
@app.get("/dashboard.html")
async def read_dashboard():
    return FileResponse(os.path.join(static_dir, 'index.html'))

# Catch-all for assets in the root mapping to static
@app.get("/{filename}")
async def get_static_file(filename: str):
    file_path = os.path.join(static_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    # Special cases
    if filename == "logo.png":
        logo_path = os.path.join(root_path, "app", "logo.png")
        if os.path.exists(logo_path):
            return FileResponse(logo_path)
    raise HTTPException(status_code=404)
