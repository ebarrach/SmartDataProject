// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.1 21/06/2025)
// =============================================
window.onload = async () => {
    try {
        const response = await fetch("/factures");
        const factures = await response.json();
        const table = document.querySelector("#factures-table tbody");
        table.innerHTML = (factures.map(f => `
            <tr>
                <td>${f.id_facture}</td>
                <td>${f.date_emission}</td>
                <td>${f.montant_facture} €</td>
                <td>${f.statut}</td>
                <td>${f.reference_banque}</td>
            </tr>
        `).join("")) || `<tr><td colspan="5" style="text-align:center;">Aucune facture</td></tr>`;
    } catch (e) {
        console.error("Erreur de chargement des factures :", e);
        const table = document.querySelector("#factures-table tbody");
        if (table) {
            table.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
    }
};
