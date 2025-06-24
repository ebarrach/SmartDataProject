// ================================
//   Chargement dynamique Factures
//   ================================
window.onload = async () => {
    try {
        // Appel API REST pour récupérer la liste des factures
        const response = await fetch("/factures");
        const factures = await response.json();
        const tableBody = document.querySelector("#factures-table tbody");

        if (Array.isArray(factures) && factures.length > 0) {
            tableBody.innerHTML = factures.map(f => `
                <tr>
                    <td>${f.id_facture}</td>
                    <td>${f.date_emission}</td>
                    <td>${f.montant_facture} €</td>
                    <td>${f.statut}</td>
                    <td>${f.reference_banque}</td>
                </tr>
            `).join("");
        } else {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Aucune facture</td></tr>`;
        }
    } catch (e) {
        console.error("Erreur de chargement des factures :", e);
        const tableBody = document.querySelector("#factures-table tbody");
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
    }
};
