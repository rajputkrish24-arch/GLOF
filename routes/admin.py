from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.lake import LakeModel
from models.disaster import DisasterReportModel
from models.user import UserModel
from models.alert import AlertModel
from models.zone import CriticalZoneModel, EvacuationCenterModel
from services.risk_service import RiskService
from services.data_service import ExternalDataService
from services.alert_service import AlertService
from ml.ml_model import GLOFMLModel
from ml.train_model import train_and_save_model
from database.db import query_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'ADMIN':
            flash("Access denied. Admin credentials required.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    lakes = LakeModel.get_all() or []
    status = RiskService.get_overall_system_status()
    reports = DisasterReportModel.get_all_reports() or []
    zones = CriticalZoneModel.get_all_active() or []
    users = UserModel.get_all_users() or []
    alerts = AlertModel.get_all_alerts() or []

    weather_data = ExternalDataService.fetch_imd_weather_data()

    return render_template(
        'admin_dashboard.html',
        status=status,
        lakes=lakes,
        reports=reports,
        critical_zones_count=len(zones),
        total_users=len(users),
        alerts=alerts[:5],
        weather=weather_data
    )


@admin_bp.route('/lakes', methods=['GET', 'POST'])
@admin_required
def lake_data():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('lake_name', '').strip()
            location = request.form.get('location', '').strip()
            lat = float(request.form.get('latitude', 30.0))
            lng = float(request.form.get('longitude', 79.0))
            area = float(request.form.get('lake_area_sqkm', 1.0))
            level = float(request.form.get('water_level_m', 10.0))
            temp = float(request.form.get('temperature_c', 14.0))
            rain = float(request.form.get('rainfall_mm', 10.0))
            risk = request.form.get('current_risk', 'NORMAL')
            
            LakeModel.create_lake(name, location, lat, lng, area, level, temp, rain, risk)
            flash(f"Glacial Lake '{name}' added successfully.", "success")
            
        elif action == 'edit':
            lake_id = int(request.form.get('lake_id'))
            area = float(request.form.get('lake_area_sqkm'))
            level = float(request.form.get('water_level_m'))
            temp = float(request.form.get('temperature_c'))
            rain = float(request.form.get('rainfall_mm'))
            risk = request.form.get('current_risk')
            
            LakeModel.update_lake(lake_id, area, level, temp, rain, risk)
            flash("Lake parameters updated successfully.", "info")
            
        elif action == 'delete':
            lake_id = int(request.form.get('lake_id'))
            LakeModel.delete_lake(lake_id)
            flash("Lake entry deleted.", "warning")

        elif action == 'refresh_external':
            # Fetch latest data from external IMD/SACHET service and sync
            weather = ExternalDataService.fetch_imd_weather_data()
            lakes = LakeModel.get_all()
            for l in lakes:
                # Update rainfall/temp from live fetch
                LakeModel.update_lake(
                    l['id'],
                    l['lake_area_sqkm'],
                    l['water_level_m'],
                    weather.get('temperature_c', l['temperature_c']),
                    weather.get('rainfall_24h_mm', l['rainfall_mm'])
                )
            flash(f"Data successfully synced from external source: {weather.get('source', 'External API')}", "success")

        return redirect(url_for('admin.lake_data'))

    lakes = LakeModel.get_all() or []
    return render_template('lake_data.html', lakes=lakes)


@admin_bp.route('/rainfall')
@admin_required
def rainfall():
    weather_data = ExternalDataService.fetch_imd_weather_data()
    lakes = LakeModel.get_all() or []
    return render_template('rainfall.html', weather=weather_data, lakes=lakes)


@admin_bp.route('/temperature')
@admin_required
def temperature():
    weather_data = ExternalDataService.fetch_imd_weather_data()
    lakes = LakeModel.get_all() or []
    return render_template('temperature.html', weather=weather_data, lakes=lakes)


@admin_bp.route('/risk-management', methods=['GET', 'POST'])
@admin_required
def risk_management():
    if request.method == 'POST':
        lake_id = int(request.form.get('lake_id'))
        new_risk = request.form.get('new_risk')
        reason = request.form.get('reason', 'Manual Admin Override').strip()

        lake = LakeModel.get_by_id(lake_id)
        if lake:
            LakeModel.update_risk_level(lake_id, new_risk, session['user_id'], reason)
            
            # Dispatch alert to users if escalated
            if new_risk in ['MODERATE', 'CRITICAL']:
                AlertService.dispatch_lake_risk_alert(lake['lake_name'], new_risk, lake_id)
                
            flash(f"Risk level for '{lake['lake_name']}' updated to '{new_risk}'. System alert dispatched.", "warning")

        return redirect(url_for('admin.risk_management'))

    lakes = LakeModel.get_all() or []
    history = LakeModel.get_risk_history() or []
    return render_template('risk_management.html', lakes=lakes, history=history)


@admin_bp.route('/critical-zones', methods=['GET', 'POST'])
@admin_required
def critical_zones():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('zone_name', '').strip()
            lat = float(request.form.get('latitude', 30.0))
            lng = float(request.form.get('longitude', 79.0))
            radius = float(request.form.get('radius_km', 2.0))
            risk = request.form.get('risk_level', 'CRITICAL')
            reason = request.form.get('reason', '').strip()

            CriticalZoneModel.create_zone(name, lat, lng, radius, risk, reason, session['user_id'])
            flash(f"Critical Danger Zone '{name}' created.", "success")
        elif action == 'toggle':
            zone_id = int(request.form.get('zone_id'))
            is_active = int(request.form.get('is_active'))
            CriticalZoneModel.toggle_zone(zone_id, is_active)
            flash("Zone active state updated.", "info")
        elif action == 'delete':
            zone_id = int(request.form.get('zone_id'))
            CriticalZoneModel.delete_zone(zone_id)
            flash("Danger zone removed.", "warning")

        return redirect(url_for('admin.critical_zones'))

    zones = CriticalZoneModel.get_all() or []
    return render_template('critical_zones.html', zones=zones)


@admin_bp.route('/evacuation-management', methods=['GET', 'POST'])
@admin_required
def evacuation_management():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name', '').strip()
            location = request.form.get('location', '').strip()
            lat = float(request.form.get('latitude'))
            lng = float(request.form.get('longitude'))
            capacity = int(request.form.get('capacity', 500))
            phone = request.form.get('phone', '').strip()

            EvacuationCenterModel.create_center(name, location, lat, lng, capacity, phone)
            flash(f"Evacuation Shelter '{name}' added.", "success")
        elif action == 'delete':
            center_id = int(request.form.get('center_id'))
            EvacuationCenterModel.delete_center(center_id)
            flash("Evacuation Shelter removed.", "info")

        return redirect(url_for('admin.evacuation_management'))

    centers = EvacuationCenterModel.get_all() or []
    return render_template('evacuation_management.html', centers=centers)


@admin_bp.route('/alerts', methods=['GET', 'POST'])
@admin_required
def alerts_admin():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        alert_type = request.form.get('alert_type', 'WARNING')
        lake_id = request.form.get('lake_id')
        lake_id_val = int(lake_id) if lake_id else None

        AlertModel.create_alert(title, message, alert_type, lake_id_val)
        flash("Emergency alert broadcasted to all users.", "success")
        return redirect(url_for('admin.alerts_admin'))

    alerts = AlertModel.get_all_alerts() or []
    lakes = LakeModel.get_all() or []
    return render_template('alerts_admin.html', alerts=alerts, lakes=lakes)


@admin_bp.route('/users')
@admin_required
def users():
    users_list = UserModel.get_all_users() or []
    return render_template('users.html', users=users_list)


@admin_bp.route('/analytics')
@admin_required
def analytics():
    ml_model = GLOFMLModel()
    sample_prediction = ml_model.predict_risk(
        rainfall_24h=85.0, temp_c=18.5, water_level_m=16.2, lake_area_sqkm=2.4, level_rise_rate=1.1
    )
    lakes = LakeModel.get_all() or []
    return render_template('analytics.html', prediction=sample_prediction, lakes=lakes)


@admin_bp.route('/train-ml', methods=['POST'])
@admin_required
def train_ml():
    try:
        acc = train_and_save_model()
        return jsonify({"status": "success", "message": f"ML Model re-trained successfully! Accuracy: {acc * 100:.2f}%"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        # Update configurable thresholds
        from config import Config
        Config.RAINFALL_MODERATE_MM = float(request.form.get('rain_mod', Config.RAINFALL_MODERATE_MM))
        Config.RAINFALL_CRITICAL_MM = float(request.form.get('rain_crit', Config.RAINFALL_CRITICAL_MM))
        Config.TEMP_MODERATE_C = float(request.form.get('temp_mod', Config.TEMP_MODERATE_C))
        Config.TEMP_CRITICAL_C = float(request.form.get('temp_crit', Config.TEMP_CRITICAL_C))
        Config.DATA_MODE = request.form.get('data_mode', Config.DATA_MODE)

        flash("System thresholds and settings updated successfully.", "success")
        return redirect(url_for('admin.settings'))

    from config import Config
    return render_template('settings.html', config=Config)
