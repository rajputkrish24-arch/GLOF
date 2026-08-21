import os
from flask import Flask, render_template, session
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

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_blueprint if 'admin_blueprint' in locals() else admin_bp)
app.register_blueprint(disaster_bp)
app.register_blueprint(evacuation_bp)
app.register_blueprint(api_bp)

# Global context processor for alerts banner & system status
@app.context_processor
def inject_global_vars():
    system_status = RiskService.get_overall_system_status()
    active_alerts = AlertModel.get_active_alerts() or []
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
    lakes = LakeModel.get_all() or []
    status = RiskService.get_overall_system_status()
    alerts = AlertModel.get_active_alerts() or []
    weather = ExternalDataService.fetch_imd_weather_data()
    
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
    print("[GLOF System] Initializing database & seed data...")
    init_db()
    print("[GLOF System] Starting Flask server on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
