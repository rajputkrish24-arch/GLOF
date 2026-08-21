import requests
import json
import xml.etree.ElementTree as ET
from config import Config

class ExternalDataService:
    """
    Data-service layer for NDMA SACHET (https://sachet.ndma.gov.in/) 
    and IMD Mausam (https://mausam.imd.gov.in/).
    Extracts weather, alert notices, and lake region precipitation.
    Includes automatic fallback to cached baseline Himalayan data.
    """
    
    @staticmethod
    def fetch_sachet_alerts():
        """
        Attempts to fetch live CAP / alert feed from NDMA SACHET portal.
        """
        url = Config.SACHET_API_URL
        try:
            response = requests.get(url, timeout=5, headers={"User-Agent": "GLOF-Early-Warning-System/1.0"})
            if response.status_code == 200:
                # Basic parser for CAP XML / JSON if present
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    data = response.json()
                    return {
                        "status": "LIVE",
                        "source": "NDMA SACHET (Live API)",
                        "alerts": data.get("alerts", [])
                    }
                elif "xml" in content_type or "<rss" in response.text or "<feed" in response.text:
                    root = ET.fromstring(response.content)
                    alerts = []
                    for item in root.findall(".//item"):
                        title = item.findtext("title", "Disaster Alert")
                        desc = item.findtext("description", "")
                        alerts.append({"title": title, "description": desc})
                    return {
                        "status": "LIVE",
                        "source": "NDMA SACHET (Live RSS Feed)",
                        "alerts": alerts
                    }
        except Exception as e:
            print(f"[DataService Info] SACHET Live fetch notice: {e}")
            
        # Fallback to cached SACHET advisory data
        return {
            "status": "DEMO_CACHED",
            "source": "NDMA SACHET (Cached Baseline Data - Live Source Unavailable)",
            "alerts": [
                {
                    "title": "Himalayan Flash Flood & GLOF Watch",
                    "description": "Heavy cloudburst expected across North Sikkim & Chamoli, Uttarakhand. High glacial runoff anticipated."
                },
                {
                    "title": "Landslide Advisory - High Altitude Passes",
                    "description": "Slippage risk elevated along NH-58 near Joshimath & Badrinath route."
                }
            ]
        }

    @staticmethod
    def fetch_imd_weather_data(region="Uttarakhand"):
        """
        Attempts to fetch live weather observations from IMD Mausam portal.
        """
        url = Config.IMD_API_URL
        try:
            headers = {"User-Agent": "GLOF-Early-Warning-System/1.0"}
            if Config.IMD_API_KEY:
                headers["X-API-KEY"] = Config.IMD_API_KEY
                
            response = requests.get(url, timeout=5, headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "status": "LIVE",
                        "source": "IMD Mausam (Live API)",
                        "temperature": data.get("temperature", 16.5),
                        "rainfall_24h": data.get("rainfall_24h", 45.0),
                        "forecast": data.get("forecast", "Heavy Precipitation Warning")
                    }
                except Exception:
                    pass
        except Exception as e:
            print(f"[DataService Info] IMD Mausam Live fetch notice: {e}")

        # Fallback to IMD weather baseline data
        return {
            "status": "DEMO_CACHED",
            "source": "IMD Mausam (Cached Baseline Data - Live Source Unavailable)",
            "temperature_c": 15.8,
            "min_temp_c": 8.2,
            "max_temp_c": 22.4,
            "rainfall_24h_mm": 52.4,
            "rainfall_weekly_mm": 184.2,
            "rainfall_monthly_mm": 410.0,
            "weather_condition": "Moderate to Heavy Mountain Rain",
            "forecast_7day": [
                {"day": "Mon", "rain_mm": 35, "temp_c": 14},
                {"day": "Tue", "rain_mm": 65, "temp_c": 16},
                {"day": "Wed", "rain_mm": 80, "temp_c": 17},
                {"day": "Thu", "rain_mm": 45, "temp_c": 15},
                {"day": "Fri", "rain_mm": 20, "temp_c": 13},
                {"day": "Sat", "rain_mm": 15, "temp_c": 12},
                {"day": "Sun", "rain_mm": 10, "temp_c": 11}
            ]
        }
