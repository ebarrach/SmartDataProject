FROM python:3.11-slim

WORKDIR /app

# Copier le code source
COPY ./app ./app
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Lancer l'application avec uvicorn en mode reload (développement)
CMD ["sh", "-c", "echo 'API disponible sur http://localhost:8000' && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
