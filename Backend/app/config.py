import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_URL = os.getenv("DATABASE_URL")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")