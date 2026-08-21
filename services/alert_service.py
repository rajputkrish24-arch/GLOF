from models.alert import AlertModel

class AlertService:
    @staticmethod
    def dispatch_lake_risk_alert(lake_name, new_risk, lake_id=None):
        """
        Dispatches an automatic system alert whenever a lake risk level escalates.
        """
        if new_risk == "CRITICAL":
            title = f"EMERGENCY ALERT: {lake_name} CRITICAL RISK"
            message = f"Immediate warning: Glacial lake '{lake_name}' has reached CRITICAL outburst risk. Heavy precipitation and water level surge detected. Check safe evacuation routes immediately."
            alert_type = "CRITICAL"
        elif new_risk == "MODERATE":
            title = f"WARNING ADVISORY: {lake_name} MODERATE RISK"
            message = f"Advisory notice: Glacial lake '{lake_name}' status updated to MODERATE risk. Enhanced monitoring in progress."
            alert_type = "WARNING"
        else:
            title = f"STATUS UPDATE: {lake_name} NORMALIZED"
            message = f"Glacial lake '{lake_name}' condition has returned to NORMAL parameters."
            alert_type = "INFO"
            
        return AlertModel.create_alert(title, message, alert_type, lake_id)

    @staticmethod
    def get_user_feed():
        return AlertModel.get_active_alerts()
