import requests

OPENROUTER_API_KEY = "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"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",
    "Content-Type": "application/json"
}

payload = {
    "model": "mistralai/mistral-small-3.2-24b-instruct:free",  # ✅ Gratuit et puissant
    "messages": [
        {"role": "user", "content": "Écris une fonction Python qui extrait toutes les adresses e-mail d’un texte."}
    ]
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

if response.status_code == 200:
    print("✅ Réponse de l'IA :\n")
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("❌ Erreur :", response.status_code)
    print(response.text)
