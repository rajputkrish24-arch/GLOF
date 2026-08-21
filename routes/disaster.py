import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models.disaster import DisasterReportModel
from models.zone import CriticalZoneModel
from config import Config

disaster_bp = Blueprint('disaster', __name__, url_prefix='/disaster')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to submit or view disaster reports.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'ADMIN':
            flash("Admin privilege required.", "danger")
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated


@disaster_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report_disaster():
    if request.method == 'POST':
        user_name = request.form.get('user_name', session.get('user_name', 'Anonymous')).strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        disaster_type = request.form.get('disaster_type', 'Flood')
        severity = request.form.get('severity', 'Medium')
        description = request.form.get('description', '').strip()
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        
        lat_val = float(lat) if lat else 30.7350
        lng_val = float(lng) if lng else 79.0650

        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                image_url = f"/static/uploads/{filename}"

        report_id = DisasterReportModel.create_report(
            user_id=session['user_id'],
            user_name=user_name,
            phone=phone,
            location=location,
            disaster_type=disaster_type,
            severity=severity,
            description=description,
            lat=lat_val,
            lng=lng_val,
            image_url=image_url
        )

        flash(f"Your disaster report has been successfully submitted. Report ID: {report_id}", "success")
        return redirect(url_for('disaster.report_history'))

    return render_template('disaster_report.html')


@disaster_bp.route('/history')
@login_required
def report_history():
    reports = DisasterReportModel.get_user_reports(session['user_id']) or []
    return render_template('report_history.html', reports=reports)


@disaster_bp.route('/admin/manage', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    if request.method == 'POST':
        report_id = request.form.get('report_id')
        new_status = request.form.get('status')
        admin_response = request.form.get('admin_response', '').strip()
        make_critical_zone = request.form.get('make_critical_zone') == '1'

        rep = DisasterReportModel.get_by_report_id(report_id)
        if rep:
            DisasterReportModel.update_status(report_id, new_status, admin_response)
            
            # If admin verified & marked as critical zone, auto-create a Critical Danger Zone
            if make_critical_zone and rep.get('latitude') and rep.get('longitude'):
                CriticalZoneModel.create_zone(
                    zone_name=f"Hazard Zone: {rep['disaster_type']} ({rep['location']})",
                    lat=rep['latitude'],
                    lng=rep['longitude'],
                    radius_km=2.0,
                    risk_level="CRITICAL" if rep['severity'] in ['High', 'Critical'] else "MODERATE",
                    reason=f"Verified Disaster Report ({report_id}): {rep['description']}",
                    admin_id=session['user_id']
                )
                flash(f"Report {report_id} updated and converted to an Active Critical Danger Zone!", "success")
            else:
                flash(f"Report {report_id} status updated to '{new_status}'.", "info")
                
        return redirect(url_for('disaster.admin_reports'))

    all_reports = DisasterReportModel.get_all_reports() or []
    return render_template('reports.html', reports=all_reports)
