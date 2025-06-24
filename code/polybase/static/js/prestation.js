window.onload = async () => {
    try {
        const response = await fetch("/prestation");
        const prestations = await response.json();
        const table = document.querySelector("#prestation-table tbody");
        table.innerHTML = (prestations.map(pre => `
            <tr>
                <td>${pre.id_prestation}</td>
                <td>${pre.date}</td>
                <td>${pre.id_tache}</td>
                <td>${pre.id_collaborateur}</td>
                <td>${pre.heures_effectuees}</td>
                <td>${pre.mode_facturation}</td>
                <td>${pre.facture_associee || '-'}</td>
                <td>${pre.taux_horaire} €</td>
            </tr>
        `).join("")) || `<tr><td colspan="8" style="text-align:center;">Aucune prestation</td></tr>`;
    } catch (e) {
        console.error("Erreur de chargement des prestations :", e);
        const table = document.querySelector("#prestation-table tbody");
        if (table) {
            table.innerHTML = `<tr><td colspan="8" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
    }
};
