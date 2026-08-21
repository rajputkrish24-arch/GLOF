from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import UserModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        location = request.form.get('location', '').strip()

        if not full_name or not email or not phone or not password:
            flash("All required fields must be filled out.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        existing_user = UserModel.get_by_email(email)
        if existing_user:
            flash("An account with this email address already exists.", "warning")
            return render_template('register.html')

        UserModel.create_user(full_name, email, phone, password, location)
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = UserModel.get_by_email(email)
        if not user or not UserModel.verify_password(user['password_hash'], password):
            flash("Invalid email address or password.", "danger")
            return render_template('login.html')

        # Set session parameters securely
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        session['user_location'] = user['location'] or "Kedarnath Basin"

        flash(f"Welcome back, {user['full_name']}!", "success")

        if user['role'] == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('index'))
