// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.1 21/06/2025)
// =============================================
window.onload = async () => {
    try {
        const response = await fetch("/planifications");
        const planifications = await response.json();
        const table = document.querySelector("#planifications-table tbody");
        table.innerHTML = (planifications.map(p => `
            <tr>
                <td>${p.id_planification}</td>
                <td>${p.id_tache}</td>
                <td>${p.id_collaborateur}</td>
                <td>${p.heures_prevues}</td>
                <td>${p.semaine}</td>
            </tr>
        `).join("")) || `<tr><td colspan="5" style="text-align:center;">Aucune planification</td></tr>`;
    } catch (e) {
        console.error("Erreur de chargement des planifications :", e);
        const table = document.querySelector("#planifications-table tbody");
        if (table) {
            table.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
    }
};
