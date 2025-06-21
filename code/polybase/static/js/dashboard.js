window.onload = async () => {
    try {
        const retard = await fetch("/dashboard/tasks/alertes").then(res => res.json());
        document.getElementById("tasks-retard").textContent = retard.taches_retard;

        const depasse = await fetch("/dashboard/heures-depassees").then(res => res.json());
        document.getElementById("heures-depassees").textContent = depasse.heures_depassees_totales;

        const facturation = await fetch("/dashboard/facturation").then(res => res.json());
        const list = facturation.map(p => `
            <p><strong>${p.id_projet}</strong> : ${p.montant_facturable_actuel} € / ${p.montant_projete} €</p>
        `).join('');
        document.getElementById("facturation").innerHTML = list;
    } catch (e) {
        console.error("Erreur chargement dashboard", e);
    }
};
