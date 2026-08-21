import os
from dotenv import load_dotenv

load_dotenv()

def get_sqlite_path():
    # If explicitly set in environment
    if os.getenv("SQLITE_PATH"):
        return os.getenv("SQLITE_PATH")
    
    # Check if running in Vercel or other serverless environments (read-only filesystem)
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp/glof.db"
    
    default_path = os.path.join(os.path.dirname(__file__), "database", "glof.db")
    try:
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        test_file = os.path.join(os.path.dirname(default_path), ".test_write")
        with open(test_file, "w") as f:
            f.write("ok")
        if os.path.exists(test_file):
            os.remove(test_file)
        return default_path
    except Exception:
        return "/tmp/glof.db"

def get_upload_folder():
    if os.getenv("UPLOAD_FOLDER"):
        return os.getenv("UPLOAD_FOLDER")
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        upload_dir = "/tmp/uploads"
    else:
        upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    try:
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    except Exception:
        fallback = "/tmp/uploads"
        try:
            os.makedirs(fallback, exist_ok=True)
        except Exception:
            pass
        return fallback

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "glof_disaster_warning_system_secret_key_2026")
    
    # Database
    USE_MYSQL = os.getenv("USE_MYSQL", "False").lower() in ("true", "1", "t")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "glof_db")
    SQLITE_PATH = get_sqlite_path()
    
    # Data Sources
    SACHET_API_URL = os.getenv("SACHET_API_URL", "https://sachet.ndma.gov.in/")
    IMD_API_URL = os.getenv("IMD_API_URL", "https://mausam.imd.gov.in/")
    IMD_API_KEY = os.getenv("IMD_API_KEY", "")
    DATA_MODE = os.getenv("DATA_MODE", "LIVE_WITH_FALLBACK")
    
    # Google Maps API Key (Optional, Leaflet.js is used by default)
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Uploads
    UPLOAD_FOLDER = get_upload_folder()
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # Default Risk Thresholds (Configurable by Admin)
    RAINFALL_MODERATE_MM = 30.0   # mm in 24h
    RAINFALL_CRITICAL_MM = 75.0   # mm in 24h
    TEMP_MODERATE_C = 20.0        # High temperature triggering rapid snow/ice melt
    TEMP_CRITICAL_C = 28.0
    WATER_LEVEL_RISE_MODERATE_M = 0.5 # Meter rise
    WATER_LEVEL_RISE_CRITICAL_M = 1.2
