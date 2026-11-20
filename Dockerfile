# =====================================================
# Dockerfile multi-stage pour l'API To-Do Flask
# =====================================================

# Version de Python choisie au moment du build (3.12 par défaut)
# Jenkins pourra la changer pour construire en parallèle (3.12 et 3.13)
ARG PYTHON_VERSION=3.12

# ---------- ÉTAPE 1 : "builder" (installe les dépendances) ----------
FROM python:${PYTHON_VERSION}-slim AS builder

# Dossier de travail dans le conteneur
WORKDIR /build

# Copier uniquement la liste des dépendances
COPY requirements.txt .

# Installer Flask dans un dossier séparé (/install)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- ÉTAPE 2 : image finale (légère) ----------
FROM python:${PYTHON_VERSION}-slim

# Version de l'application (remplie par Jenkins avec le tag vX.Y.Z)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app

# Récupérer seulement les dépendances déjà installées à l'étape 1
COPY --from=builder /install /usr/local

# Copier le code de l'application
COPY app.py .

# Créer un utilisateur sans droits administrateur (bonne pratique de sécurité)
RUN useradd --create-home appuser
USER appuser

# L'application écoute sur le port 5000
EXPOSE 5000

# Commande lancée au démarrage du conteneur
CMD ["python", "app.py"]