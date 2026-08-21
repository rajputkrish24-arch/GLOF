-- GLOF Early Warning & Disaster Management System Schema
-- Compatible with MySQL 5.7+ / MySQL 8.0 and SQLite fallback

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'USER', -- 'USER' or 'ADMIN'
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
    current_risk VARCHAR(20) NOT NULL DEFAULT 'NORMAL', -- 'NORMAL', 'MODERATE', 'CRITICAL'
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
    severity VARCHAR(20) NOT NULL, -- 'Low', 'Medium', 'High', 'Critical'
    description TEXT NOT NULL,
    image_url VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'Submitted', -- 'Submitted', 'Under Review', 'Verified', 'Resolved', 'Rejected'
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
    risk_level VARCHAR(20) NOT NULL DEFAULT 'CRITICAL', -- 'MODERATE', 'CRITICAL'
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
    alert_type VARCHAR(20) NOT NULL DEFAULT 'WARNING', -- 'INFO', 'WARNING', 'CRITICAL'
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
