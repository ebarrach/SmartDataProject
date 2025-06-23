// ==============================
// FINANCE DASHBOARD SCRIPT
// ==============================

document.addEventListener("DOMContentLoaded", () => {
    console.log("📊 Chargement du tableau financier...");
    fetchDepassements();
    fetchAlertes();
    fetchBudgets();
});

// --- Dépassements par projet ---
function fetchDepassements() {
    fetch("/api/finance/depassements")
        .then(res => res.json())
        .then(data => {
            const couleursDepassements = data.data.map(h =>
                h <= 2 ? "#F5CCCC" : "#AA3939"
            );

            new Chart(document.getElementById("chartDepassements"), {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Heures dépassées",
                        data: data.data,
                        backgroundColor: couleursDepassements
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: "Heures dépassées par projet" },
                        legend: { display: true }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: "Heures" }
                        },
                        x: {
                            title: { display: true, text: "Projets" }
                        }
                    }
                }
            });
        });
}

// --- Alertes de retard ---
function fetchAlertes() {
    fetch("/api/finance/alertes")
        .then(res => res.json())
        .then(data => {
            const alertesData = data.data.map(v => v === 0 ? 0.01 : v);
            const couleursAlertes = data.data.map(a =>
                a === 0 ? "#B8E9B8" : a === 1 ? "#F5CCCC" : "#AA3939"
            );

            new Chart(document.getElementById("chartAlertes"), {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Alertes",
                        data: alertesData,
                        backgroundColor: couleursAlertes
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: "Alertes de tâches en retard" },
                        legend: { position: 'bottom' }
                    }
                }
            });
        });
}

// --- Budgets vs Coûts (colonnes comparatives) ---
function fetchBudgets() {
    fetch("/api/finance/budgets")
        .then(res => res.json())
        .then(data => {
            const couleursCouts = data.labels.map((_, i) =>
                data.cout[i] <= data.budget[i] ? "rgba(102,180,102,0.8)" : "rgba(214,80,80,0.8)"
            );

            new Chart(document.getElementById("chartBudgets"), {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: "Budget alloué (€)",
                            data: data.budget,
                            backgroundColor: "rgba(102,180,102,0.6)" // Vert doux
                        },
                        {
                            label: "Coûts actuels (€)",
                            data: data.cout,
                            backgroundColor: couleursCouts
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: "Budgets vs Coûts par projet" },
                        legend: { position: 'bottom' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: "Montant (€)" }
                        },
                        x: {
                            title: { display: true, text: "Projets" }
                        }
                    }
                }
            });
        });
}
