// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.1 21/06/2025)
// =============================================
// ----- Script de gestion de la page Détail Tâche -----
document.addEventListener("DOMContentLoaded", () => {
    const btnComplete = document.getElementById("mark-complete");
    const btnSave = document.getElementById("save-comment");

    // Fonction : conversion des statuts techniques vers lisibles
    function formatStatut(val) {
        switch (val) {
            case "a_faire": return "À faire";
            case "en_cours": return "En cours";
            case "termine": return "Terminé";
            default: return val;
        }
    }

    // Exemple de remplissage de la section statut (à relier plus tard à l'API)
    const statut = "en_cours"; // valeur simulée - à remplacer par data.statut
    document.getElementById("task-status").innerText = formatStatut(statut);

    // Action : marquer la tâche comme terminée
    btnComplete.addEventListener("click", () => {
        alert("Tâche marquée comme terminée (simulé)");
        // Tu pourrais faire un fetch PUT ici
    });

    // Action : enregistrer un commentaire
    btnSave.addEventListener("click", () => {
        const comment = document.getElementById("comment").value;
        alert("Commentaire enregistré : " + comment);
        // fetch POST pour commentaire si stocké
    });
});
