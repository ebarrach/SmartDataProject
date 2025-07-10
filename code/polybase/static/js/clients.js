// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.1 21/06/2025)
// =============================================
window.onload = async () => {
    try {
        const response = await fetch("/clients");
        const clients = await response.json();
        const table = document.querySelector("#clients-table tbody");
        table.innerHTML = (clients.map(c => `
            <tr>
                <td>${c.id_client}</td>
                <td>${c.nom_client}</td>
                <td>${c.adresse}</td>
                <td>${c.secteur_activite}</td>
            </tr>
        `).join("")) || `<tr><td colspan="4" style="text-align:center;">Aucun client</td></tr>`;
    } catch (e) {
        console.error("Erreur de chargement des clients :", e);
        const table = document.querySelector("#clients-table tbody");
        if (table) {
            table.innerHTML = `<tr><td colspan="4" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
    }
};
