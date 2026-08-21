from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        return query_db("SELECT id, full_name, email, phone, role, location, created_at FROM users WHERE id = %s", (user_id,), one=True)

    @staticmethod
    def get_by_email(email):
        return query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)

    @staticmethod
    def create_user(full_name, email, phone, password, location=""):
        password_hash = generate_password_hash(password)
        return query_db(
            "INSERT INTO users (full_name, email, phone, password_hash, role, location) VALUES (%s, %s, %s, %s, 'USER', %s)",
            (full_name, email, phone, password_hash, location),
            commit=True
        )

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def get_all_users():
        return query_db("SELECT id, full_name, email, phone, role, location, created_at FROM users ORDER BY id DESC")
