import os
from flask import Flask, render_template, session, send_from_directory
from config import Config
from database.db import init_db
from models.lake import LakeModel
from models.alert import AlertModel
from services.risk_service import RiskService
from services.data_service import ExternalDataService

# Import Blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.disaster import disaster_bp
from routes.evacuation import evacuation_bp
from routes.api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists safely
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    print(f"[Uploads Notice] {e}")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(disaster_bp)
app.register_blueprint(evacuation_bp)
app.register_blueprint(api_bp)

# Auto-initialize database on application startup / serverless cold-start
try:
    init_db()
except Exception as e:
    print(f"[Database Auto-Init Notice] {e}")

# Serve dynamic uploads safely
@app.route('/static/uploads/<path:filename>')
def custom_uploads_serve(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Global context processor for alerts banner & system status
@app.context_processor
def inject_global_vars():
    try:
        system_status = RiskService.get_overall_system_status()
    except Exception:
        system_status = {"system_level": "NORMAL", "active_warnings": 0, "critical_lakes": 0}
        
    try:
        active_alerts = AlertModel.get_active_alerts() or []
    except Exception:
        active_alerts = []

    return dict(
        system_status=system_status,
        global_alerts=active_alerts,
        current_user=dict(
            id=session.get('user_id'),
            name=session.get('user_name'),
            role=session.get('user_role'),
            location=session.get('user_location')
        )
    )

@app.route('/')
def index():
    """
    Public Landing Page for GLOF Early Warning & Disaster Response System.
    """
    try:
        lakes = LakeModel.get_all() or []
    except Exception:
        lakes = []
        
    try:
        status = RiskService.get_overall_system_status()
    except Exception:
        status = {"system_level": "NORMAL", "active_warnings": 0, "critical_lakes": 0}
        
    try:
        alerts = AlertModel.get_active_alerts() or []
    except Exception:
        alerts = []
        
    try:
        weather = ExternalDataService.fetch_imd_weather_data()
    except Exception:
        weather = None
    
    return render_template(
        'index.html',
        status=status,
        lakes=lakes,
        alerts=alerts,
        weather=weather
    )

@app.route('/about')
def about():
    """
    About the Project & GLOF Warning System explanation.
    """
    return render_template('about.html')

@app.route('/contact')
def contact():
    """
    Emergency Helpline & Contact Directory.
    """
    return render_template('contact.html')

if __name__ == '__main__':
    print("[GLOF System] Starting Flask server on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
