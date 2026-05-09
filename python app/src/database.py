from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import os
if os.environ.get('VERCEL'):
    DATABASE_URL = "sqlite:////tmp/users.db"
else:
    DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    last_otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True) # Changed to DateTime for easier management

Base.metadata.create_all(bind=engine)

# Manually add columns if they don't exist (SQLAlchemy create_all doesn't add to existing tables)
def run_migrations():
    try:
        with engine.begin() as conn:
            # Using try-except for EACH alter command because some might already exist
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
            except Exception: pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_otp VARCHAR"))
            except Exception: pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN otp_expiry DATETIME"))
            except Exception: pass
    except Exception as e:
        print(f"Migration error: {e}")

run_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
