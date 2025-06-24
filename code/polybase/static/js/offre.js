window.onload = async () => {
    try {
        const response = await fetch("/offres");
        const offres = await response.json();

        // Statistiques
        let total = 0;
        let gagnees = 0;
        let perdues = 0;

        offres.forEach(offre => {
            total += offre.nombre || 0;
            if ((offre.indicateur || "").toLowerCase().includes("gagnée")) {
                gagnees += offre.nombre || 0;
            }
            if ((offre.indicateur || "").toLowerCase().includes("perdue")) {
                perdues += offre.nombre || 0;
            }
        });

        // Affichage stat-value
        document.getElementById("offres-total").textContent = total;
        document.getElementById("offres-gagnees").textContent = gagnees;
        document.getElementById("offres-perdues").textContent = perdues;

        // Remplissage tableau
        const table = document.querySelector("#offres-table tbody");
        table.innerHTML = (offres.map(o => `
            <tr>
                <td>${o.annee}</td>
                <td>${o.entite}</td>
                <td>${o.type_marche}</td>
                <td>${o.indicateur || '-'}</td>
                <td>${o.nombre}</td>
            </tr>
        `).join("")) || `<tr><td colspan="5" style="text-align:center;">Aucune offre</td></tr>`;
    } catch (e) {
        console.error("Erreur de chargement des offres :", e);
        const table = document.querySelector("#offres-table tbody");
        if (table) {
            table.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#c00;">Erreur de chargement</td></tr>`;
        }
        document.getElementById("offres-total").textContent = "-";
        document.getElementById("offres-gagnees").textContent = "-";
        document.getElementById("offres-perdues").textContent = "-";
    }
};
