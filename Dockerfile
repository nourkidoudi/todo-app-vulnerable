# ============================================================
# Dockerfile — VERSION VULNÉRABLE (Phase 1 & 2 du TP)
# ============================================================
# Ce Dockerfile contient intentionnellement des failles :
#   ❌ Image de base complète (surface d'attaque maximale)
#   ❌ Exécution en tant que root
#   ❌ Copie de TOUT le répertoire (inclut .git, .env, tests)
#   ❌ Secret hardcodé dans ENV
#   ❌ Mode DEBUG activé
#   ❌ Serveur de développement Flask en production
#   ❌ Pas de HEALTHCHECK
#   ❌ Port 5000 (privilégié sur certains systèmes)
#   ❌ Pas de .dockerignore adapté
# ============================================================

FROM python:3.11

WORKDIR /app

# ❌ Copie TOUT le contenu (y compris .git, .env, fichiers de test)
COPY . .

# ❌ Installation sans --no-cache-dir (augmente la taille de l'image)
RUN pip install -r requirements.txt

# ❌ Secrets hardcodés dans le Dockerfile
ENV SECRET_KEY="hardcoded-secret-key-do-not-use-123"
ENV ADMIN_API_KEY="admin-key-12345"
ENV JWT_SECRET="jwt-secret-hardcoded"

# ❌ Mode debug activé — expose des informations sensibles
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development

EXPOSE 5000

# ❌ Serveur de développement Flask — ne jamais utiliser en production
CMD ["python", "-m", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
