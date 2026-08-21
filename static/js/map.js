// Leaflet Interactive Map Module for GLOF Warning System

function initGLOFMap(elementId, centerLat = 30.7350, centerLng = 79.0650, zoomLevel = 9) {
    if (typeof L === 'undefined') {
        console.error("[GLOF Map Error] Leaflet library not loaded.");
        return null;
    }

    const map = L.map(elementId).setView([centerLat, centerLng], zoomLevel);

    // OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors | GLOF Early Warning System'
    }).addTo(map);

    return map;
}

function addLakesToMap(map, lakes) {
    if (!map || !lakes) return;

    lakes.forEach(lake => {
        let color = '#16a34a'; // Green NORMAL
        if (lake.current_risk === 'MODERATE') color = '#d97706'; // Yellow
        if (lake.current_risk === 'CRITICAL') color = '#dc2626'; // Red

        const marker = L.circleMarker([lake.latitude, lake.longitude], {
            radius: 10,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(map);

        const popupContent = `
            <div style="min-width: 180px;">
                <h6 style="margin: 0 0 6px 0; font-weight:700;">${lake.lake_name}</h6>
                <span class="badge-status badge-${lake.current_risk.toLowerCase()}">${lake.current_risk} RISK</span>
                <hr style="margin:6px 0;">
                <small>
                    <b>Location:</b> ${lake.location}<br>
                    <b>Water Level:</b> ${lake.water_level_m} m<br>
                    <b>Lake Area:</b> ${lake.lake_area_sqkm} sq km<br>
                    <b>Temp:</b> ${lake.temperature_c} °C<br>
                    <b>Rainfall:</b> ${lake.rainfall_mm} mm
                </small>
                <div style="margin-top:8px;">
                    <a href="/user/lakes/${lake.id}" class="btn btn-sm btn-primary w-100 py-1 style="font-size:0.75rem;">View Analytics</a>
                </div>
            </div>
        `;
        marker.bindPopup(popupContent);
    });
}

function addCriticalZonesToMap(map, zones) {
    if (!map || !zones) return;

    zones.forEach(zone => {
        const radiusMeters = (zone.radius_km || 2.0) * 1000;
        const color = zone.risk_level === 'CRITICAL' ? '#dc2626' : '#d97706';

        // Draw translucent danger circle
        L.circle([zone.latitude, zone.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.25,
            radius: radiusMeters
        }).addTo(map);

        L.marker([zone.latitude, zone.longitude]).addTo(map)
            .bindPopup(`<b>⚠️ ${zone.zone_name}</b><br>Risk: ${zone.risk_level}<br>Radius: ${zone.radius_km} km<br>Reason: ${zone.reason}`);
    });
}

function addEvacuationCentersToMap(map, centers) {
    if (!map || !centers) return;

    centers.forEach(center => {
        L.marker([center.latitude, center.longitude]).addTo(map)
            .bindPopup(`<b>🏥 ${center.name}</b><br>Capacity: ${center.capacity} people<br>Phone: ${center.contact_phone || 'N/A'}`);
    });
}

function drawRoutePolylines(map, routes) {
    if (!map || !routes) return;

    routes.forEach(route => {
        let pathColor = '#16a34a'; // Green SAFE
        if (route.status === 'MODERATE RISK') pathColor = '#d97706';
        if (route.status === 'HIGH RISK') pathColor = '#dc2626';

        const polyline = L.polyline(route.waypoints, {
            color: pathColor,
            weight: route.path_id === 'PATH_A' ? 6 : 4,
            opacity: 0.85,
            dashArray: route.status === 'HIGH RISK' ? '5, 10' : null
        }).addTo(map);

        polyline.bindPopup(`<b>${route.name}</b><br>Score: ${route.risk_score}/100<br>Status: ${route.status}`);
    });
}
