// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.2 11/07/2025)
// =============================================

document.addEventListener("DOMContentLoaded", async () => {
    const days = ["Lun", "Mar", "Mer", "Jeu", "Ven"];
    const container = document.getElementById("weekly-view");
    const taskList = document.getElementById("task-list");

    // Initialiser colonnes vides
    const dayColumns = {};
    days.forEach(day => {
        const col = document.createElement("div");
        col.className = "day-column";
        col.innerHTML = `<h4>${day}</h4><div class="day-content" id="content-${day}"></div>`;
        container.appendChild(col);
        dayColumns[day] = col.querySelector(".day-content");
    });

    // Convertit une date ISO en nom de jour FR
    function getDayName(isoDateStr) {
        const date = new Date(isoDateStr);
        const jsDay = date.getDay(); // 0=Dim, 1=Lun...
        return ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"][jsDay];
    }

    // Charge les événements Outlook depuis l’API
    try {
        const res = await fetch("/outlook/events");
        const events = await res.json();

        events.forEach(ev => {
            const day = getDayName(ev.date_debut);
            if (dayColumns[day]) {
                const item = document.createElement("div");
                item.className = "agenda-event";
                item.textContent = `${ev.sujet} (${ev.date_debut.slice(11, 16)} - ${ev.date_fin.slice(11, 16)})`;
                dayColumns[day].appendChild(item);
            }
        });
    } catch (err) {
        console.error("Erreur chargement Outlook :", err);
    }

    // Charge les tâches à planifier
    try {
        const res = await fetch("/tasks/agenda");
        const tasks = await res.json();

        tasks.forEach(task => {
            const li = document.createElement("li");
            li.textContent = task.nom_tache || task.titre || "Tâche";
            taskList.appendChild(li);
        });
    } catch (err) {
        console.error("Erreur chargement tâches :", err);
    }
});
