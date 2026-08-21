from flask import Blueprint, render_template, request, jsonify, session
from services.route_service import RouteService
from models.zone import CriticalZoneModel, EvacuationCenterModel
from models.lake import LakeModel
from models.disaster import DisasterReportModel

evacuation_bp = Blueprint('evacuation', __name__, url_prefix='/evacuation')

@evacuation_bp.route('/')
def evacuation_page():
    centers = EvacuationCenterModel.get_all_active() or []
    lakes = LakeModel.get_all() or []
    return render_template('evacuation.html', centers=centers, lakes=lakes)


@evacuation_bp.route('/map')
def map_page():
    lakes = LakeModel.get_all() or []
    zones = CriticalZoneModel.get_all_active() or []
    centers = EvacuationCenterModel.get_all_active() or []
    reports = [r for r in (DisasterReportModel.get_all_reports() or []) if r['status'] == 'Verified']
    
    return render_template(
        'map.html',
        lakes=lakes,
        zones=zones,
        centers=centers,
        reports=reports
    )


@evacuation_bp.route('/calculate', methods=['POST'])
def calculate_route():
    data = request.get_json() or request.form
    origin = data.get('origin', 'Kedarnath Town')
    destination = data.get('destination', 'Kedarnath Relief Base Alpha')
    
    result = RouteService.calculate_route_risk(origin, destination)
    
    # If user logged in, log route query history
    if 'user_id' in session:
        from database.db import query_db
        query_db(
            "INSERT INTO route_history (user_id, origin, destination, recommended_path, risk_score) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], origin, destination, result['recommended_route']['path_id'], result['recommended_route']['risk_score']),
            commit=True
        )

    return jsonify(result)
