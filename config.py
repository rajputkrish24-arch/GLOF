import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "glof_disaster_warning_system_secret_key_2026")
    
    # Database
    USE_MYSQL = os.getenv("USE_MYSQL", "False").lower() in ("true", "1", "t")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "glof_db")
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "database", "glof.db")
    
    # Data Sources
    SACHET_API_URL = os.getenv("SACHET_API_URL", "https://sachet.ndma.gov.in/")
    IMD_API_URL = os.getenv("IMD_API_URL", "https://mausam.imd.gov.in/")
    IMD_API_KEY = os.getenv("IMD_API_KEY", "")
    DATA_MODE = os.getenv("DATA_MODE", "LIVE_WITH_FALLBACK")
    
    # Google Maps API Key (Optional, Leaflet.js is used by default)
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # Default Risk Thresholds (Configurable by Admin)
    RAINFALL_MODERATE_MM = 30.0   # mm in 24h
    RAINFALL_CRITICAL_MM = 75.0   # mm in 24h
    TEMP_MODERATE_C = 20.0        # High temperature triggering rapid snow/ice melt
    TEMP_CRITICAL_C = 28.0
    WATER_LEVEL_RISE_MODERATE_M = 0.5 # Meter rise
    WATER_LEVEL_RISE_CRITICAL_M = 1.2
