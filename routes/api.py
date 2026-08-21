from flask import Blueprint, jsonify, request, session, Response
from models.lake import LakeModel
from models.disaster import DisasterReportModel
from models.alert import AlertModel
from models.user import UserModel
from models.zone import CriticalZoneModel, EvacuationCenterModel
from services.risk_service import RiskService
from services.route_service import RouteService
from services.data_service import ExternalDataService
from ml.ml_model import GLOFMLModel

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/lakes', methods=['GET'])
def get_lakes():
    lakes = LakeModel.get_all() or []
    return jsonify(lakes)


@api_bp.route('/lakes/<int:lake_id>', methods=['GET'])
def get_lake(lake_id):
    lake = LakeModel.get_by_id(lake_id)
    if not lake:
        return jsonify({"error": "Lake not found"}), 404
    return jsonify(lake)


@api_bp.route('/lakes/<int:lake_id>/history', methods=['GET'])
def get_lake_history(lake_id):
    history = LakeModel.get_measurements_history(lake_id) or []
    return jsonify(history)


@api_bp.route('/risk', methods=['GET'])
def get_system_risk():
    status = RiskService.get_overall_system_status()
    return jsonify(status)


@api_bp.route('/reports', methods=['GET', 'POST'])
def reports_api():
    if request.method == 'POST':
        data = request.get_json() or {}
        rep_id = DisasterReportModel.create_report(
            user_id=session.get('user_id'),
            user_name=data.get('user_name', 'API User'),
            phone=data.get('phone', 'N/A'),
            location=data.get('location', 'Unknown'),
            disaster_type=data.get('disaster_type', 'Flood'),
            severity=data.get('severity', 'Medium'),
            description=data.get('description', ''),
            lat=data.get('latitude'),
            lng=data.get('longitude')
        )
        return jsonify({"message": "Report created", "report_id": rep_id}), 201
        
    reports = DisasterReportModel.get_all_reports() or []
    return jsonify(reports)


@api_bp.route('/routes/calculate', methods=['POST'])
def calculate_route_api():
    data = request.get_json() or {}
    origin = data.get('origin', 'Kedarnath')
    dest = data.get('destination', 'Relief Shelter Alpha')
    result = RouteService.calculate_route_risk(origin, dest)
    return jsonify(result)


@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = AlertModel.get_active_alerts() or []
    return jsonify(alerts)


@api_bp.route('/predict-ml', methods=['POST'])
def predict_ml_api():
    data = request.get_json() or {}
    ml = GLOFMLModel()
    res = ml.predict_risk(
        rainfall_24h=float(data.get('rainfall_24h', 50.0)),
        temp_c=float(data.get('temp_c', 15.0)),
        water_level_m=float(data.get('water_level_m', 12.0)),
        lake_area_sqkm=float(data.get('lake_area_sqkm', 1.5)),
        level_rise_rate=float(data.get('level_rise_rate', 0.5))
    )
    return jsonify(res)


@api_bp.route('/admin/statistics', methods=['GET'])
def admin_stats():
    status = RiskService.get_overall_system_status()
    weather = ExternalDataService.fetch_imd_weather_data()
    return jsonify({
        "status": status,
        "weather_source": weather.get("source"),
        "rainfall_24h": weather.get("rainfall_24h_mm")
    })


@api_bp.route('/export-db', methods=['GET'])
def export_db():
    """
    Exports full database contents (Users, Glacial Lakes, Disaster Reports, Critical Zones) in JSON format.
    """
    users = UserModel.get_all_users() or []
    lakes = LakeModel.get_all() or []
    reports = DisasterReportModel.get_all_reports() or []
    zones = CriticalZoneModel.get_all_active() or []
    centers = EvacuationCenterModel.get_all_active() or []

    export_data = {
        "system_info": "GLOF Early Warning & Disaster Response Database Dump",
        "users": users,
        "lakes": lakes,
        "disaster_reports": reports,
        "critical_zones": zones,
        "evacuation_centers": centers
    }
    return jsonify(export_data)
