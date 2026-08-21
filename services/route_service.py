import math
from models.zone import CriticalZoneModel, EvacuationCenterModel
from models.disaster import DisasterReportModel
from models.lake import LakeModel

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance in kilometers between two lat/lon coordinates.
    """
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RouteService:
    @staticmethod
    def calculate_route_risk(origin_name, destination_name, origin_coords=None, dest_coords=None):
        """
        Calculates safety scores for multiple candidate evacuation routes.
        Evaluates:
          1. Rainfall Risk factor
          2. Critical Flood Zone proximity
          3. Glacial Lake outburst status
          4. Verified user road blockage / landslide reports
          5. Route distance & elevation time factor
        Normalizes final score:
          0 - 30: SAFE
          31 - 60: MODERATE RISK
          61 - 100: HIGH RISK
        """
        # Fetch active danger zones and verified disaster reports
        critical_zones = CriticalZoneModel.get_all_active() or []
        verified_reports = [r for r in (DisasterReportModel.get_all_reports() or []) if r['status'] == 'Verified']
        critical_lakes = [l for l in (LakeModel.get_all() or []) if l['current_risk'] in ['MODERATE', 'CRITICAL']]

        # Define candidate paths for demonstration/routing
        # Path A (High-altitude bypass route avoiding river beds)
        # Path B (Main Valley road along river basin)
        # Path C (Shortest direct mountain trek path near active landslide zone)
        
        candidate_paths = [
            {
                "path_id": "PATH_A",
                "name": "Path A - Ridge Bypass Highway",
                "distance_km": 4.8,
                "est_time_mins": 15,
                "elevation_gain_m": 80,
                "waypoints": [
                    [30.7350, 79.0650],
                    [30.7300, 79.0720],
                    [30.7220, 79.0780],
                    [30.7150, 79.0820]
                ],
                "base_hazard_offset": 5
            },
            {
                "path_id": "PATH_B",
                "name": "Path B - Main River Valley Route",
                "distance_km": 4.1,
                "est_time_mins": 13,
                "elevation_gain_m": 20,
                "waypoints": [
                    [30.7350, 79.0650],
                    [30.7310, 79.0620],
                    [30.7250, 79.0590],
                    [30.7150, 79.0820]
                ],
                "base_hazard_offset": 30
            },
            {
                "path_id": "PATH_C",
                "name": "Path C - Direct Gorge Pass",
                "distance_km": 3.7,
                "est_time_mins": 11,
                "elevation_gain_m": 120,
                "waypoints": [
                    [30.7350, 79.0650],
                    [30.7280, 79.0600],
                    [30.7200, 79.0650],
                    [30.7150, 79.0820]
                ],
                "base_hazard_offset": 55
            }
        ]

        evaluated_routes = []

        for path in candidate_paths:
            rainfall_risk = 10
            flood_zone_risk = 0
            lake_risk = 0
            road_blockage_risk = 0
            distance_factor = round(path["distance_km"] * 1.5, 1)

            hazards_detected = []

            # 1. Check proximity to Admin Critical Zones
            for zone in critical_zones:
                z_lat, z_lng = float(zone['latitude']), float(zone['longitude'])
                z_radius = float(zone['radius_km'])
                
                # Check if any waypoint intersects danger circle
                for wp in path["waypoints"]:
                    dist = haversine_distance(wp[0], wp[1], z_lat, z_lng)
                    if dist <= z_radius:
                        penalty = 40 if zone['risk_level'] == 'CRITICAL' else 20
                        flood_zone_risk += penalty
                        hazards_detected.append(f"Passes within {round(dist, 1)}km of Critical Danger Zone '{zone['zone_name']}'")
                        break

            # 2. Check proximity to Critical Glacial Lakes
            for lake in critical_lakes:
                l_lat, l_lng = float(lake['latitude']), float(lake['longitude'])
                for wp in path["waypoints"]:
                    dist = haversine_distance(wp[0], wp[1], l_lat, l_lng)
                    if dist <= 10.0: # Within 10km downstream corridor
                        penalty = 30 if lake['current_risk'] == 'CRITICAL' else 15
                        lake_risk += penalty
                        hazards_detected.append(f"Located in downstream outburst path of {lake['lake_name']} ({lake['current_risk']} Risk)")
                        break

            # 3. Check Verified User Disaster Reports (Landslide/Road Blockage)
            for rep in verified_reports:
                if rep.get('latitude') and rep.get('longitude'):
                    r_lat, r_lng = float(rep['latitude']), float(rep['longitude'])
                    for wp in path["waypoints"]:
                        dist = haversine_distance(wp[0], wp[1], r_lat, r_lng)
                        if dist <= 1.5:
                            road_blockage_risk += 25
                            hazards_detected.append(f"Active report: '{rep['disaster_type']}' near route ({rep['severity']} Severity)")
                            break

            # Calculate total raw risk score
            raw_score = path["base_hazard_offset"] + rainfall_risk + flood_zone_risk + lake_risk + road_blockage_risk + distance_factor
            normalized_score = min(100, max(0, int(raw_score)))

            # Safety Level classification
            if normalized_score <= 30:
                status = "SAFE"
                status_class = "success"
                recommendation = "RECOMMENDED SAFEST ROUTE"
            elif normalized_score <= 60:
                status = "MODERATE RISK"
                status_class = "warning"
                recommendation = "USE WITH CAUTION"
            else:
                status = "HIGH RISK"
                status_class = "danger"
                recommendation = "NOT RECOMMENDED (DANGER ZONE)"

            evaluated_routes.append({
                "path_id": path["path_id"],
                "name": path["name"],
                "distance_km": path["distance_km"],
                "est_time_mins": path["est_time_mins"],
                "risk_score": normalized_score,
                "status": status,
                "status_class": status_class,
                "recommendation": recommendation,
                "waypoints": path["waypoints"],
                "hazards_detected": hazards_detected if hazards_detected else ["No severe hazards detected along this route."],
                "breakdown": {
                    "rainfall_risk": rainfall_risk,
                    "flood_zone_risk": flood_zone_risk,
                    "lake_risk": lake_risk,
                    "road_blockage_risk": road_blockage_risk,
                    "distance_factor": distance_factor
                }
            })

        # Sort routes so safest is first
        evaluated_routes.sort(key=lambda r: r["risk_score"])
        
        return {
            "origin": origin_name,
            "destination": destination_name,
            "recommended_route": evaluated_routes[0],
            "all_routes": evaluated_routes
        }
