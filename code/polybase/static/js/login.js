document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const response = await fetch("/login", {
            method: "POST",
            body: formData
        });

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const html = await response.text();
            document.documentElement.innerHTML = html; // Recharge la page avec l’erreur
        }
    });
});
