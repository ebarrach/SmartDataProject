document.addEventListener("DOMContentLoaded", () => {
    // Simule un chargement de l'agenda
    const days = ["Lun", "Mar", "Mer", "Jeu", "Ven"];
    const container = document.getElementById("weekly-view");

    days.forEach(day => {
        const col = document.createElement("div");
        col.className = "day-column";
        col.innerHTML = `<h4>${day}</h4><div class="day-content">Aucune tâche</div>`;
        container.appendChild(col);
    });

    // Tâches à droite
    const taskList = document.getElementById("task-list");
    const tasks = ["Préparer audit", "Rédiger rapport", "Réunion client"];
    tasks.forEach(t => {
        const li = document.createElement("li");
        li.textContent = t;
        taskList.appendChild(li);
    });
});
