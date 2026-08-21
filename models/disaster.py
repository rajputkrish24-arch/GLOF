import random
from database.db import query_db

class DisasterReportModel:
    @staticmethod
    def generate_report_id():
        num = random.randint(10000, 99999)
        return f"GLOF-REPORT-{num}"

    @staticmethod
    def create_report(user_id, user_name, phone, location, disaster_type, severity, description, lat=None, lng=None, image_url=None):
        rep_id = DisasterReportModel.generate_report_id()
        query_db(
            "INSERT INTO disaster_reports (report_id, user_id, user_name, phone, location, latitude, longitude, disaster_type, severity, description, image_url, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted')",
            (rep_id, user_id, user_name, phone, location, lat, lng, disaster_type, severity, description, image_url),
            commit=True
        )
        return rep_id

    @staticmethod
    def get_user_reports(user_id):
        return query_db("SELECT * FROM disaster_reports WHERE user_id = %s ORDER BY created_at DESC", (user_id,))

    @staticmethod
    def get_all_reports():
        return query_db("SELECT * FROM disaster_reports ORDER BY created_at DESC")

    @staticmethod
    def get_by_report_id(report_id):
        return query_db("SELECT * FROM disaster_reports WHERE report_id = %s", (report_id,), one=True)

    @staticmethod
    def update_status(report_id, status, admin_response=None):
        query_db(
            "UPDATE disaster_reports SET status = %s, admin_response = %s WHERE report_id = %s",
            (status, admin_response, report_id),
            commit=True
        )
