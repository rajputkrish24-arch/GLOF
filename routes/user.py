from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.lake import LakeModel
from models.alert import AlertModel
from models.user import UserModel
from models.disaster import DisasterReportModel
from services.risk_service import RiskService
from services.data_service import ExternalDataService

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access your user dashboard.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route('/dashboard')
@user_required
def dashboard():
    lakes = LakeModel.get_all() or []
    status_summary = RiskService.get_overall_system_status()
    alerts = AlertModel.get_active_alerts() or []
    user_reports = DisasterReportModel.get_user_reports(session['user_id']) or []
    
    # External IMD/SACHET data status
    weather_data = ExternalDataService.fetch_imd_weather_data()
    
    return render_template(
        'user_dashboard.html',
        status=status_summary,
        lakes=lakes,
        alerts=alerts,
        user_reports=user_reports[:5],
        weather=weather_data
    )


@user_bp.route('/lakes')
@user_required
def lake_conditions():
    lakes = LakeModel.get_all() or []
    return render_template('user_lakes.html', lakes=lakes)


@user_bp.route('/lakes/<int:lake_id>')
@user_required
def lake_details(lake_id):
    lake = LakeModel.get_by_id(lake_id)
    if not lake:
        flash("Lake not found.", "danger")
        return redirect(url_for('user.lake_conditions'))
        
    history = LakeModel.get_measurements_history(lake_id, limit=30) or []
    risk_history = LakeModel.get_risk_history(lake_id) or []
    
    return render_template(
        'lake_details.html',
        lake=lake,
        history=history,
        risk_history=risk_history
    )


@user_bp.route('/alerts')
@user_required
def alerts():
    alerts_list = AlertModel.get_all_alerts() or []
    return render_template('alerts.html', alerts=alerts_list)


@user_bp.route('/profile', methods=['GET', 'POST'])
@user_required
def profile():
    user = UserModel.get_by_id(session['user_id'])
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        
        # Update user session and DB
        from database.db import query_db
        query_db(
            "UPDATE users SET full_name = %s, phone = %s, location = %s WHERE id = %s",
            (full_name, phone, location, session['user_id']),
            commit=True
        )
        session['user_name'] = full_name
        session['user_location'] = location
        flash("Profile updated successfully!", "success")
        return redirect(url_for('user.profile'))

    return render_template('profile.html', user=user)
