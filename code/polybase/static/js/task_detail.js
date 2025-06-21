// ----- Script de gestion de la page Détail Tâche -----
document.addEventListener("DOMContentLoaded", () => {
    const btnComplete = document.getElementById("mark-complete");
    const btnSave = document.getElementById("save-comment");

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
