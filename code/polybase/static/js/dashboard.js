// ----- Chargement des données du tableau de bord -----
window.onload = async () => {
    try {
        // Tâches en retard
        const retard = await fetch("/dashboard/tasks/alertes").then(res => res.json());
        const tasksEl = document.getElementById("tasks-retard");
        if (tasksEl) tasksEl.textContent = retard.taches_retard ?? '0';

        // Heures dépassées
        const depasse = await fetch("/dashboard/heures-depassees").then(res => res.json());
        const heuresEl = document.getElementById("heures-depassees");
        if (heuresEl) heuresEl.textContent = depasse.heures_depassees_totales ?? '0';

        // Facturation
        const facturation = await fetch("/dashboard/facturation").then(res => res.json());
        const factureEl = document.getElementById("facturation");
        if (factureEl) {
            const list = facturation.map(p =>
                `<p><strong>${p.id_projet}</strong> : ${p.montant_facturable_actuel ?? 0} € / ${p.montant_projete ?? 0} €</p>`
            ).join('');
            factureEl.innerHTML = list;
        }

    } catch (e) {
        console.error("Erreur de chargement du tableau de bord :", e);
    }
};

