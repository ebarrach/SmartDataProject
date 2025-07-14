import requests

# 🔐 Ton token API DeepSeek à placer ici
DEEPSEEK_API_KEY = "sk-a5a3168e045b4fd282dee01b0bad5376"  # Remplace par ta vraie clé API

# 📩 Corps de la requête
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",  # ou deepseek-coder selon le besoin
    "messages": [
        {"role": "system", "content": "Tu es un assistant expert en Python."},
        {"role": "user", "content": "Écris une fonction pour extraire les adresses e-mail d’un texte."}
    ],
    "temperature": 0.7
}

# 🔁 Envoi de la requête
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers=headers,
    json=payload
)

# 📤 Résultat
if response.status_code == 200:
    data = response.json()
    print("✅ Réponse de DeepSeek :")
    print(data["choices"][0]["message"]["content"])
else:
    print("❌ Erreur :", response.status_code)
    print(response.text)
