// Dashboard Interactive Scripts
document.addEventListener("DOMContentLoaded", function() {
    console.log("[GLOF Dashboard] System loaded & active.");
    
    // Auto refresh risk status every 60 seconds
    setInterval(refreshSystemStatus, 60000);
});

function refreshSystemStatus() {
    fetch('/api/risk')
        .then(res => res.json())
        .then(data => {
            console.log("[GLOF Status Update]", data);
            const statusBadge = document.getElementById("global-system-status-badge");
            if (statusBadge) {
                statusBadge.textContent = "SYSTEM STATUS: " + data.system_status;
                statusBadge.className = "badge-status badge-" + data.badge_class;
            }
        })
        .catch(err => console.error("[GLOF Status Error]", err));
}
