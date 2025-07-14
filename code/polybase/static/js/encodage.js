// Chargement dynamique des projets
document.addEventListener("DOMContentLoaded", () => {
    const selectProjet = document.getElementById("id_projet");
    fetch("/admin/table/Projet")
        .then(res => res.json())
        .then(data => {
            selectProjet.innerHTML = '<option value="">-- Sélectionner un projet --</option>';
            data.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id_projet;
                opt.textContent = `${p.nom_projet} (${p.id_projet})`;
                selectProjet.appendChild(opt);
            });
        })
        .catch(() => {
            selectProjet.innerHTML = '<option value="">Erreur de chargement</option>';
        });
});
