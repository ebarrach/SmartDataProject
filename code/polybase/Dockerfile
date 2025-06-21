FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y gcc libmariadb-dev

# Créer un dossier de travail
WORKDIR /app

# Copier le contenu de l'app
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Lancer l'application FastAPI avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
