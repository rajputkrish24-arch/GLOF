from database.db import query_db

class CriticalZoneModel:
    @staticmethod
    def get_all_active():
        return query_db("SELECT * FROM critical_zones WHERE is_active = 1 ORDER BY created_at DESC")

    @staticmethod
    def get_all():
        return query_db("SELECT * FROM critical_zones ORDER BY created_at DESC")

    @staticmethod
    def get_by_id(zone_id):
        return query_db("SELECT * FROM critical_zones WHERE id = %s", (zone_id,), one=True)

    @staticmethod
    def create_zone(zone_name, lat, lng, radius_km, risk_level, reason, admin_id=None):
        return query_db(
            "INSERT INTO critical_zones (zone_name, latitude, longitude, radius_km, risk_level, reason, is_active, created_by) VALUES (%s, %s, %s, %s, %s, %s, 1, %s)",
            (zone_name, lat, lng, radius_km, risk_level, reason, admin_id),
            commit=True
        )

    @staticmethod
    def toggle_zone(zone_id, is_active):
        query_db("UPDATE critical_zones SET is_active = %s WHERE id = %s", (is_active, zone_id), commit=True)

    @staticmethod
    def delete_zone(zone_id):
        query_db("DELETE FROM critical_zones WHERE id = %s", (zone_id,), commit=True)


class EvacuationCenterModel:
    @staticmethod
    def get_all_active():
        return query_db("SELECT * FROM evacuation_centers WHERE is_active = 1 ORDER BY name ASC")

    @staticmethod
    def get_all():
        return query_db("SELECT * FROM evacuation_centers ORDER BY name ASC")

    @staticmethod
    def create_center(name, location, lat, lng, capacity, phone):
        return query_db(
            "INSERT INTO evacuation_centers (name, location, latitude, longitude, capacity, contact_phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, 1)",
            (name, location, lat, lng, capacity, phone),
            commit=True
        )

    @staticmethod
    def delete_center(center_id):
        query_db("DELETE FROM evacuation_centers WHERE id = %s", (center_id,), commit=True)
