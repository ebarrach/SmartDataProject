// =============================================
// specification: Esteban Barracho (v.1 21/06/2025)
// implement: Esteban Barracho (v.1 21/06/2025)
// =============================================
// ----- Script de gestion du formulaire de connexion -----
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");

    // Interception de la soumission du formulaire
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Envoi des données via fetch
        const formData = new FormData(form);
        const response = await fetch("/login", {
            method: "POST",
            body: formData
        });

        // Redirection ou affichage d’erreur
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const html = await response.text();
            document.documentElement.innerHTML = html; // Recharge avec le message d'erreur
        }
    });
});
