document.addEventListener("DOMContentLoaded", () => {
    const btnComplete = document.getElementById("mark-complete");
    const btnSave = document.getElementById("save-comment");

    btnComplete.addEventListener("click", () => {
        alert("Tâche marquée comme terminée (simulé)");
        // Tu pourrais faire un fetch PUT ici
    });

    btnSave.addEventListener("click", () => {
        const comment = document.getElementById("comment").value;
        alert("Commentaire enregistré : " + comment);
        // fetch POST pour commentaire si stocké
    });
});
