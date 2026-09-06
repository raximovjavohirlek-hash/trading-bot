import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    
    # API Keys
    GOLDAPI_KEY: str = os.getenv("GOLDAPI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    DB_PATH: Path = BASE_DIR / "gold_market.db"
    
    # Data Polling & Quality
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
    MAX_SPREAD_THRESHOLD: float = float(os.getenv("MAX_SPREAD_THRESHOLD", "15.0")) # $15 max spread alert
    STALE_PRICE_SECONDS: int = int(os.getenv("STALE_PRICE_SECONDS", "300")) # 5 min stale check
    
    # AI Cost Optimization
    AI_MIN_INTERVAL_MINUTES: int = int(os.getenv("AI_MIN_INTERVAL_MINUTES", "30")) # minimum 30 min between scheduled AI calls
    
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            print("⚠️ WARNING: TELEGRAM_BOT_TOKEN topilmadi! .env faylida o'rnating.")
        if not cls.GOLDAPI_KEY:
            print("ℹ️ INFO: GOLDAPI_KEY kiritilmagan. Fallback (Yahoo Finance API) ishlatiladi.")
        if not cls.GEMINI_API_KEY:
            print("ℹ️ INFO: GEMINI_API_KEY kiritilmagan. AI rejimi qisman to'xtatiladi yoki heuristic analitik ishlatiladi.")

settings = Settings()
