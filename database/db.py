import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import Config

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    location VARCHAR(150),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lakes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lake_name VARCHAR(150) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    lake_area_sqkm DECIMAL(8, 2) NOT NULL DEFAULT 1.5,
    water_level_m DECIMAL(8, 2) NOT NULL DEFAULT 12.4,
    temperature_c DECIMAL(5, 2) NOT NULL DEFAULT 14.2,
    rainfall_mm DECIMAL(6, 2) NOT NULL DEFAULT 12.0,
    current_risk VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lake_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lake_id INT NOT NULL,
    water_level_m DECIMAL(8, 2) NOT NULL,
    lake_area_sqkm DECIMAL(8, 2) NOT NULL,
    temperature_c DECIMAL(5, 2) NOT NULL,
    rainfall_mm DECIMAL(6, 2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lake_id) REFERENCES lakes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rainfall_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    current_mm DECIMAL(6, 2) NOT NULL,
    daily_mm DECIMAL(6, 2) NOT NULL,
    weekly_mm DECIMAL(6, 2) NOT NULL,
    monthly_mm DECIMAL(6, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS temperature_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    current_c DECIMAL(5, 2) NOT NULL,
    min_c DECIMAL(5, 2) NOT NULL,
    max_c DECIMAL(5, 2) NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS disaster_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id VARCHAR(30) NOT NULL UNIQUE,
    user_id INT,
    user_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    location VARCHAR(150) NOT NULL,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    disaster_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'Submitted',
    admin_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS critical_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(150) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    radius_km DECIMAL(6, 2) NOT NULL DEFAULT 2.0,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'CRITICAL',
    reason TEXT NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evacuation_centers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(150) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    capacity INT NOT NULL DEFAULT 500,
    contact_phone VARCHAR(30),
    is_active TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS risk_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lake_id INT NOT NULL,
    previous_risk VARCHAR(20) NOT NULL,
    new_risk VARCHAR(20) NOT NULL,
    changed_by_admin_id INT,
    reason TEXT NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lake_id) REFERENCES lakes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    alert_type VARCHAR(20) NOT NULL DEFAULT 'WARNING',
    lake_id INT,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS route_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    origin VARCHAR(150) NOT NULL,
    destination VARCHAR(150) NOT NULL,
    recommended_path VARCHAR(50) NOT NULL,
    risk_score INT NOT NULL,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def get_db_connection():
    """
    Returns a database connection based on Config.USE_MYSQL setting.
    Falls back gracefully to SQLite if MySQL is unavailable or misconfigured.
    """
    if Config.USE_MYSQL:
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
            return conn, "MYSQL"
        except Exception as e:
            print(f"[DB Warning] Failed to connect to MySQL ({e}). Falling back to SQLite database.")
    
    # SQLite Fallback Connection
    db_path = Config.SQLITE_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn, "SQLITE"


def query_db(query, args=(), one=False, commit=False):
    """
    Executes a database query with parameterized arguments.
    Returns dictionaries for rows to unify SQLite and MySQL interfaces.
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # Adjust placeholders if SQLite vs MySQL
    if db_type == "SQLITE":
        query_formatted = query.replace("%s", "?")
    else:
        query_formatted = query
        
    try:
        cursor.execute(query_formatted, args)
        if commit:
            if db_type == "SQLITE":
                conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
            
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return (results[0] if results else None) if one else results
        else:
            cursor.close()
            conn.close()
            return None
    except Exception as e:
        print(f"[DB Error] Query execution failed: {e}\nQuery: {query_formatted}\nArgs: {args}")
        if db_type == "SQLITE":
            try:
                conn.rollback()
            except Exception:
                pass
        cursor.close()
        conn.close()
        raise e


def init_db():
    """
    Initializes database schema and seeds initial Himalayan glacial lakes and admin user.
    """
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()
        else:
            schema_sql = SCHEMA_SQL
            
        if db_type == "SQLITE":
            sqlite_schema = schema_sql.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            sqlite_schema = sqlite_schema.replace("TINYINT(1)", "INTEGER")
            sqlite_schema = sqlite_schema.replace("DATETIME DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            cursor.executescript(sqlite_schema)
            conn.commit()
        else:
            statements = schema_sql.split(';')
            for stmt in statements:
                if stmt.strip():
                    cursor.execute(stmt)
            conn.commit()
            
        cursor.close()
        conn.close()
        
        seed_default_data()
    except Exception as e:
        print(f"[DB Initialization Notice]: {e}")


def seed_default_data():
    """
    Seeds initial default admin account, user account, Himalayan lakes, and evacuation centers if empty.
    """
    try:
        # Check if admin user exists
        admin_user = query_db("SELECT * FROM users WHERE role = 'ADMIN'", one=True)
        if not admin_user:
            admin_pass = generate_password_hash("admin123")
            query_db(
                "INSERT INTO users (full_name, email, phone, password_hash, role, location) VALUES (%s, %s, %s, %s, %s, %s)",
                ("System Administrator", "admin@glof.gov.in", "+91 9876543210", admin_pass, "ADMIN", "Dehradun Control Center"),
                commit=True
            )
            
        # Check default user
        demo_user = query_db("SELECT * FROM users WHERE role = 'USER'", one=True)
        if not demo_user:
            user_pass = generate_password_hash("user123")
            query_db(
                "INSERT INTO users (full_name, email, phone, password_hash, role, location) VALUES (%s, %s, %s, %s, %s, %s)",
                ("Rajesh Sharma", "user@glof.gov.in", "+91 9812345678", user_pass, "USER", "Kedarnath Valley"),
                commit=True
            )
            
        # Seed Lakes if empty
        existing_lakes = query_db("SELECT COUNT(*) as cnt FROM lakes", one=True)
        if not existing_lakes or existing_lakes.get("cnt", 0) == 0:
            lakes_data = [
                ("Chorabari Lake", "Kedarnath, Uttarakhand", 30.7380, 79.0620, 1.85, 14.2, 16.5, 45.0, "MODERATE"),
                ("South Lhonak Lake", "North Sikkim, Sikkim", 27.9150, 88.2040, 2.40, 18.6, 12.0, 85.5, "CRITICAL"),
                ("Imja Tsho", "Khumbu, High Himalayas", 27.9000, 86.9200, 1.28, 11.5, 8.4, 18.0, "NORMAL"),
                ("Lake Tsho Lhamo", "North Sikkim", 27.9800, 88.7500, 3.10, 15.0, 10.5, 22.0, "NORMAL"),
                ("Ghepang Gath Lake", "Lahaul Valley, Himachal Pradesh", 32.5200, 77.2100, 1.15, 9.8, 14.0, 35.0, "MODERATE")
            ]
            
            for l in lakes_data:
                lake_id = query_db(
                    "INSERT INTO lakes (lake_name, location, latitude, longitude, lake_area_sqkm, water_level_m, temperature_c, rainfall_mm, current_risk) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    l, commit=True
                )
                
                # Seed 7-day historical measurements for chart rendering
                now = datetime.now()
                for day in range(7, -1, -1):
                    timestamp = (now - timedelta(days=day)).strftime('%Y-%m-%d %H:%M:%S')
                    area_var = l[4] + (0.05 * (7 - day))
                    level_var = l[5] + (0.3 * (7 - day) if l[8] != "NORMAL" else 0.05 * (7 - day))
                    temp_var = l[6] + (0.5 * (day % 3))
                    rain_var = l[7] + (5.0 * (day % 4))
                    
                    query_db(
                        "INSERT INTO lake_measurements (lake_id, water_level_m, lake_area_sqkm, temperature_c, rainfall_mm, risk_level, recorded_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (lake_id, round(level_var, 2), round(area_var, 2), round(temp_var, 2), round(rain_var, 2), l[8], timestamp),
                        commit=True
                    )
                    
        # Seed Evacuation Centers if empty
        existing_centers = query_db("SELECT COUNT(*) as cnt FROM evacuation_centers", one=True)
        if not existing_centers or existing_centers.get("cnt", 0) == 0:
            centers = [
                ("Kedarnath Relief Base Alpha", "Upper Helipad, Kedarnath", 30.7350, 79.0680, 1200, "+91 135 2740001"),
                ("Rudraprayag Safe Relief Hub", "District Stadium, Rudraprayag", 30.2850, 78.9800, 3500, "+91 135 2740002"),
                ("Gangtok Emergency Center", "Development Area, Gangtok", 27.3300, 88.6100, 2500, "+91 3592 202001"),
                ("Manali Safe Transit Camp", "Mall Road Grounds, Manali", 32.2430, 77.1890, 2000, "+91 1902 252001")
            ]
            for c in centers:
                query_db(
                    "INSERT INTO evacuation_centers (name, location, latitude, longitude, capacity, contact_phone) VALUES (%s, %s, %s, %s, %s, %s)",
                    c, commit=True
                )

        # Seed Critical Zone if empty
        existing_zones = query_db("SELECT COUNT(*) as cnt FROM critical_zones", one=True)
        if not existing_zones or existing_zones.get("cnt", 0) == 0:
            query_db(
                "INSERT INTO critical_zones (zone_name, latitude, longitude, radius_km, risk_level, reason, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ("South Lhonak Flood Danger Zone", 27.9150, 88.2040, 3.5, "CRITICAL", "High water level surge detected following intense cloudburst precipitation.", 1),
                commit=True
            )

        # Seed Initial Alerts
        existing_alerts = query_db("SELECT COUNT(*) as cnt FROM alerts", one=True)
        if not existing_alerts or existing_alerts.get("cnt", 0) == 0:
            query_db(
                "INSERT INTO alerts (title, message, alert_type, lake_id, is_active) VALUES (%s, %s, %s, %s, %s)",
                ("CRITICAL WARNING: South Lhonak Lake Surge", "Glacial lake water level exceeds critical threshold. Heavy rainfall ongoing in North Sikkim. Downstream evacuation recommended.", "CRITICAL", 2, 1),
                commit=True
            )
            query_db(
                "INSERT INTO alerts (title, message, alert_type, lake_id, is_active) VALUES (%s, %s, %s, %s, %s)",
                ("MODERATE ADVISORY: Chorabari Lake Monitoring", "Temperatures rising rapidly over Kedarnath basin, causing accelerated snowmelt runoff.", "WARNING", 1, 1),
                commit=True
            )
    except Exception as e:
        print(f"[Seed Data Notice]: {e}")
