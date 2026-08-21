// Evacuation Route Safety Calculator JavaScript

document.addEventListener("DOMContentLoaded", function() {
    const routeForm = document.getElementById("evacuation-route-form");
    if (routeForm) {
        routeForm.addEventListener("submit", function(e) {
            e.preventDefault();
            calculateRoutes();
        });
    }
});

function calculateRoutes() {
    const origin = document.getElementById("origin-input").value || "Kedarnath";
    const destination = document.getElementById("destination-input").value || "Relief Shelter Alpha";
    const resultsContainer = document.getElementById("route-results-container");
    const loadingSpinner = document.getElementById("route-loading-spinner");

    if (loadingSpinner) loadingSpinner.style.display = "block";
    if (resultsContainer) resultsContainer.style.display = "none";

    fetch('/evacuation/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: origin, destination: destination })
    })
    .then(res => res.json())
    .then(data => {
        if (loadingSpinner) loadingSpinner.style.display = "none";
        if (resultsContainer) resultsContainer.style.display = "block";

        renderRouteCards(data);
        if (window.evacMap && data.all_routes) {
            drawRoutePolylines(window.evacMap, data.all_routes);
        }
    })
    .catch(err => {
        console.error("[Route Calc Error]", err);
        if (loadingSpinner) loadingSpinner.style.display = "none";
        alert("Failed to compute evacuation routes. Please check network connection.");
    });
}

function renderRouteCards(data) {
    const cardsWrapper = document.getElementById("route-cards-list");
    if (!cardsWrapper) return;

    let html = "";
    data.all_routes.forEach((route, idx) => {
        const isRecommended = idx === 0;
        const cardClass = isRecommended ? "route-card recommended" : (route.status === "HIGH RISK" ? "route-card high-risk" : "route-card");

        html += `
            <div class="${cardClass}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="mb-0 font-weight-bold">${route.name}</h5>
                    <span class="badge-status badge-${route.status_class}">${route.status}</span>
                </div>
                <div class="mb-2 text-muted" style="font-size: 0.9rem;">
                    <span><b>Distance:</b> ${route.distance_km} km</span> | 
                    <span><b>Est Time:</b> ${route.est_time_mins} mins</span> | 
                    <span class="text-danger font-weight-bold"><b>Risk Score:</b> ${route.risk_score} / 100</span>
                </div>
                ${isRecommended ? `<div class="alert alert-success py-1 px-2 mb-2 style="font-size:0.85rem;"><i class="bi bi-shield-check me-1"></i> <b>RECOMMENDED SAFEST EVACUATION ROUTE</b></div>` : ''}
                
                <div class="bg-light p-2 rounded mb-2" style="font-size: 0.82rem;">
                    <b>Hazards & Risk Factors:</b>
                    <ul class="mb-0 ps-3">
                        ${route.hazards_detected.map(h => `<li>${h}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    });

    cardsWrapper.innerHTML = html;
}
