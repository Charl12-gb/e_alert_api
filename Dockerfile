# Dockerfile
FROM python:3.12.2-slim

# Installer les dépendances
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    g++ \
    apache2 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . /app

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt -v

# Exposer le port 8000 pour Django
EXPOSE 8000

# Commande de démarrage de l'application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]