from config import Config
from models.lake import LakeModel
from models.disaster import DisasterReportModel

class RiskService:
    @staticmethod
    def evaluate_lake_risk(rainfall_mm, temperature_c, water_level_m, lake_area_sqkm, baseline_level=10.0):
        """
        Calculates automatic GLOF risk classification for a lake.
        Uses admin-configurable thresholds from Config.
        """
        risk_score = 0
        reasons = []

        # Rainfall evaluation
        if rainfall_mm >= Config.RAINFALL_CRITICAL_MM:
            risk_score += 40
            reasons.append(f"Critical rainfall: {rainfall_mm}mm (Threshold: {Config.RAINFALL_CRITICAL_MM}mm)")
        elif rainfall_mm >= Config.RAINFALL_MODERATE_MM:
            risk_score += 20
            reasons.append(f"Moderate rainfall: {rainfall_mm}mm")

        # Temperature evaluation (High temp causes accelerated ice melting)
        if temperature_c >= Config.TEMP_CRITICAL_C:
            risk_score += 30
            reasons.append(f"Critical high temperature melt risk: {temperature_c}°C")
        elif temperature_c >= Config.TEMP_MODERATE_C:
            risk_score += 15
            reasons.append(f"Elevated temperature melt risk: {temperature_c}°C")

        # Water level surge
        level_rise = water_level_m - baseline_level
        if level_rise >= Config.WATER_LEVEL_RISE_CRITICAL_M:
            risk_score += 35
            reasons.append(f"Critical water level surge (+{round(level_rise, 2)}m)")
        elif level_rise >= Config.WATER_LEVEL_RISE_MODERATE_M:
            risk_score += 15
            reasons.append(f"Moderate water level rise (+{round(level_rise, 2)}m)")

        # Lake area expansion
        if lake_area_sqkm > 2.0:
            risk_score += 15
            reasons.append(f"Large surface area storage volume: {lake_area_sqkm} sq km")

        # Classification decision
        if risk_score >= 50:
            risk_level = "CRITICAL"
        elif risk_score >= 25:
            risk_level = "MODERATE"
        else:
            risk_level = "NORMAL"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons
        }

    @staticmethod
    def get_overall_system_status():
        """
        Aggregates system-wide GLOF risk status across all monitored lakes and disaster reports.
        """
        lakes = LakeModel.get_all() or []
        reports = DisasterReportModel.get_all_reports() or []
        
        total_lakes = len(lakes)
        normal_lakes = sum(1 for l in lakes if l['current_risk'] == 'NORMAL')
        moderate_lakes = sum(1 for l in lakes if l['current_risk'] == 'MODERATE')
        critical_lakes = sum(1 for l in lakes if l['current_risk'] == 'CRITICAL')
        active_reports = sum(1 for r in reports if r['status'] in ['Submitted', 'Under Review', 'Verified'])

        if critical_lakes > 0 or any(r['severity'] == 'Critical' for r in reports if r['status'] == 'Verified'):
            system_status = "CRITICAL"
            badge_class = "danger"
        elif moderate_lakes > 0 or active_reports > 0:
            system_status = "MODERATE RISK"
            badge_class = "warning"
        else:
            system_status = "NORMAL"
            badge_class = "success"

        return {
            "system_status": system_status,
            "badge_class": badge_class,
            "total_lakes": total_lakes,
            "normal_lakes": normal_lakes,
            "moderate_lakes": moderate_lakes,
            "critical_lakes": critical_lakes,
            "active_reports": active_reports
        }
