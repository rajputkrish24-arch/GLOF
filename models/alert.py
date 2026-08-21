from database.db import query_db

class AlertModel:
    @staticmethod
    def get_active_alerts():
        return query_db("SELECT a.*, l.lake_name FROM alerts a LEFT JOIN lakes l ON a.lake_id = l.id WHERE a.is_active = 1 ORDER BY a.created_at DESC")

    @staticmethod
    def get_all_alerts():
        return query_db("SELECT a.*, l.lake_name FROM alerts a LEFT JOIN lakes l ON a.lake_id = l.id ORDER BY a.created_at DESC")

    @staticmethod
    def create_alert(title, message, alert_type="WARNING", lake_id=None):
        return query_db(
            "INSERT INTO alerts (title, message, alert_type, lake_id, is_active) VALUES (%s, %s, %s, %s, 1)",
            (title, message, alert_type, lake_id),
            commit=True
        )

    @staticmethod
    def toggle_alert(alert_id, is_active):
        query_db("UPDATE alerts SET is_active = %s WHERE id = %s", (is_active, alert_id), commit=True)
        
    @staticmethod
    def delete_alert(alert_id):
        query_db("DELETE FROM alerts WHERE id = %s", (alert_id,), commit=True)
