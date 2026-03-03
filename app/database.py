import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime

load_dotenv(dotenv_path="app/.env")


# Build connection to upirakshak_db
# Ensure your .env file has DB_NAME=upirakshak_db
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABLE DEFINITION FOR ML DATA ---
class UPIDataset(Base):
    __tablename__ = "upi_dataset"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    amount = Column(Float)
    is_fraud = Column(Integer)
    risk_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.now)

# Automatically create the table in pgAdmin if it doesn't exist
Base.metadata.create_all(bind=engine)