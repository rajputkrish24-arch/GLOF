from database.db import query_db
from datetime import datetime

class LakeModel:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM lakes ORDER BY lake_name ASC")

    @staticmethod
    def get_by_id(lake_id):
        return query_db("SELECT * FROM lakes WHERE id = %s", (lake_id,), one=True)

    @staticmethod
    def create_lake(lake_name, location, latitude, longitude, area, level, temp, rain, risk="NORMAL"):
        return query_db(
            "INSERT INTO lakes (lake_name, location, latitude, longitude, lake_area_sqkm, water_level_m, temperature_c, rainfall_mm, current_risk) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (lake_name, location, latitude, longitude, area, level, temp, rain, risk),
            commit=True
        )

    @staticmethod
    def update_lake(lake_id, area, level, temp, rain, risk=None):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if risk:
            query_db(
                "UPDATE lakes SET lake_area_sqkm = %s, water_level_m = %s, temperature_c = %s, rainfall_mm = %s, current_risk = %s, last_updated = %s WHERE id = %s",
                (area, level, temp, rain, risk, now, lake_id),
                commit=True
            )
        else:
            query_db(
                "UPDATE lakes SET lake_area_sqkm = %s, water_level_m = %s, temperature_c = %s, rainfall_mm = %s, last_updated = %s WHERE id = %s",
                (area, level, temp, rain, now, lake_id),
                commit=True
            )
            
        # Log measurement historical record
        current_lake = LakeModel.get_by_id(lake_id)
        effective_risk = risk if risk else (current_lake['current_risk'] if current_lake else 'NORMAL')
        query_db(
            "INSERT INTO lake_measurements (lake_id, water_level_m, lake_area_sqkm, temperature_c, rainfall_mm, risk_level, recorded_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (lake_id, level, area, temp, rain, effective_risk, now),
            commit=True
        )

    @staticmethod
    def update_risk_level(lake_id, new_risk, admin_id, reason):
        lake = LakeModel.get_by_id(lake_id)
        if not lake:
            return False
            
        prev_risk = lake['current_risk']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query_db("UPDATE lakes SET current_risk = %s, last_updated = %s WHERE id = %s", (new_risk, now, lake_id), commit=True)
        
        query_db(
            "INSERT INTO risk_history (lake_id, previous_risk, new_risk, changed_by_admin_id, reason, changed_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (lake_id, prev_risk, new_risk, admin_id, reason, now),
            commit=True
        )
        return True

    @staticmethod
    def delete_lake(lake_id):
        query_db("DELETE FROM lakes WHERE id = %s", (lake_id,), commit=True)

    @staticmethod
    def get_measurements_history(lake_id, limit=20):
        return query_db(
            "SELECT * FROM lake_measurements WHERE lake_id = %s ORDER BY recorded_at ASC LIMIT %s",
            (lake_id, limit)
        )

    @staticmethod
    def get_risk_history(lake_id=None):
        if lake_id:
            return query_db(
                "SELECT rh.*, l.lake_name, u.full_name as admin_name FROM risk_history rh JOIN lakes l ON rh.lake_id = l.id LEFT JOIN users u ON rh.changed_by_admin_id = u.id WHERE rh.lake_id = %s ORDER BY rh.changed_at DESC",
                (lake_id,)
            )
        return query_db(
            "SELECT rh.*, l.lake_name, u.full_name as admin_name FROM risk_history rh JOIN lakes l ON rh.lake_id = l.id LEFT JOIN users u ON rh.changed_by_admin_id = u.id ORDER BY rh.changed_at DESC"
        )
