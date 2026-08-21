-- =========================================================================
-- GLOF EARLY WARNING SYSTEM — COMPLETE DATABASE EXPORT & SEED SCRIPT
-- Compatible with MySQL 5.7+ / MySQL 8.0 & SQLite
-- =========================================================================

-- 1. USERS TABLE
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

INSERT INTO users (id, full_name, email, phone, password_hash, role, location) VALUES
(1, 'System Administrator', 'admin@glof.gov.in', '+91 9876543210', 'scrypt:32768:8:1$7hJ9k...$pbkdf2:sha256:admin123', 'ADMIN', 'Dehradun Control Center'),
(2, 'Rajesh Sharma', 'user@glof.gov.in', '+91 9812345678', 'scrypt:32768:8:1$9xL2p...$pbkdf2:sha256:user123', 'USER', 'Kedarnath Valley');

-- 2. LAKES TABLE
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

INSERT INTO lakes (id, lake_name, location, latitude, longitude, lake_area_sqkm, water_level_m, temperature_c, rainfall_mm, current_risk) VALUES
(1, 'South Lhonak Lake', 'North Sikkim', 27.915000, 88.204000, 2.40, 5.46, 2.10, 58.20, 'CRITICAL'),
(2, 'Thorthormi Lake', 'Gangtok', 27.850000, 88.500000, 1.80, 3.21, 1.80, 48.70, 'MODERATE'),
(3, 'Tsho Lhamo Lake', 'Lachung', 27.980000, 88.750000, 3.10, 1.98, 0.90, 22.10, 'NORMAL'),
(4, 'Dig Tsho Lake', 'West Sikkim', 27.750000, 88.150000, 1.10, 2.34, 1.20, 31.60, 'NORMAL'),
(5, 'Rathong Lake', 'East Sikkim', 27.600000, 88.400000, 1.45, 4.12, 1.60, 41.30, 'MODERATE');

-- 3. DISASTER REPORTS TABLE
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO disaster_reports (id, report_id, user_id, user_name, phone, location, latitude, longitude, disaster_type, severity, description, status) VALUES
(1, 'GLOF-REPORT-00021', 2, 'Rajesh Sharma', '+91 9812345678', 'Kedarnath Valley Corridor', 30.735000, 79.065000, 'Glacial Lake Outburst', 'Critical', 'Water level surging rapidly after torrential cloudburst precipitation near lake moraine wall.', 'Verified');

-- 4. CRITICAL ZONES TABLE
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

INSERT INTO critical_zones (id, zone_name, latitude, longitude, radius_km, risk_level, reason, is_active) VALUES
(1, 'South Lhonak Flood Danger Zone', 27.915000, 88.204000, 3.50, 'CRITICAL', 'Glacial outburst water level surge detected.', 1);

-- 5. EVACUATION CENTERS TABLE
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

INSERT INTO evacuation_centers (id, name, location, latitude, longitude, capacity, contact_phone) VALUES
(1, 'Kedarnath Relief Base Alpha', 'Upper Helipad, Kedarnath', 30.735000, 79.068000, 1200, '+91 135 2740001'),
(2, 'Rudraprayag Safe Relief Hub', 'District Stadium, Rudraprayag', 30.285000, 78.980000, 3500, '+91 135 2740002');
