// Chart.js Visualizations for Glacial Lake Analytics

function renderLakeHistoryChart(canvasId, labels, waterLevels, temperatures, rainfalls) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Water Level (m)',
                    data: waterLevels,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Rainfall (mm)',
                    data: rainfalls,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.2)',
                    borderWidth: 2,
                    type: 'bar',
                    yAxisID: 'y1'
                },
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: '#d97706',
                    borderWidth: 2,
                    pointRadius: 3,
                    yAxisID: 'y'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Level (m) / Temp (°C)' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    title: { display: true, text: 'Precipitation (mm)' }
                }
            }
        }
    });
}
