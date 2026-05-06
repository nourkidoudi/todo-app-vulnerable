# 🔐 Todo App — TP DevSecOps : Sécurisation d'une Application Conteneurisée

[![Docker Security Pipeline](https://github.com/votre-username/todo-app-vulnerable/actions/workflows/docker-security.yml/badge.svg)](https://github.com/votre-username/todo-app-vulnerable/actions)
[![Trivy](https://img.shields.io/badge/Scanned%20by-Trivy-blue)](https://trivy.dev)
[![Hadolint](https://img.shields.io/badge/Linted%20by-Hadolint-orange)](https://github.com/hadolint/hadolint)
[![Master DevOps](https://img.shields.io/badge/Master-DevOps-1565C0)](/)

> **⚠️ Application intentionnellement vulnérable à des fins pédagogiques.**
> Ne jamais déployer en production. Utiliser uniquement dans un environnement de TP isolé.

---

## 📋 Contexte pédagogique

Ce dépôt est utilisé dans le cadre du TP **"Sécurisation d'une Application Conteneurisée avec Docker"** du Master DevOps.
L'objectif est d'apprendre à **détecter, corriger et valider** les vulnérabilités d'une application web et de son environnement Docker.

**Durée du TP :** 3 heures (3 phases de 1h)

---

## 🗂️ Structure du projet

```
todo-app-vulnerable/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── routes.py            # ❌ Endpoints vulnérables (SQL, XSS, RCE…)
│   ├── models.py            # ❌ MD5 pour les mots de passe
│   └── templates/
│       └── index.html       # Interface web
├── tests/
│   └── test_app.py          # Tests fonctionnels + tests sécurité (Phase 3)
├── scripts/
│   └── seed.py              # Données de démo
├── .github/
│   └── workflows/
│       └── docker-security.yml  # Pipeline CI/CD complet
├── Dockerfile               # ❌ VERSION VULNÉRABLE (Phase 1 & 2)
├── Dockerfile.hardened      # ✅ VERSION SÉCURISÉE  (Phase 3)
├── docker-compose.yml       # ❌ VERSION VULNÉRABLE
├── docker-compose.hardened.yml  # ✅ VERSION SÉCURISÉE
├── requirements.txt         # ❌ Dépendances vulnérables
├── requirements-secure.txt  # ✅ Dépendances à jour
└── .env.example             # Template de configuration
```

---

## 🚀 Démarrage rapide

### Phase 1 — Lancer la version vulnérable

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/todo-app-vulnerable.git
cd todo-app-vulnerable

# Build et lancement
docker build -t todo-app:v1-unsafe .
docker run -d -p 5000:5000 --name todo-unsafe todo-app:v1-unsafe

# Vérifier
curl http://localhost:5000/health
# Accéder à l'interface : http://localhost:5000
```

### Phase 3 — Lancer la version sécurisée

```bash
# Générer un fichier .env
cp .env.example .env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env

# Build et lancement sécurisé
docker build -t todo-app:v2-hardened -f Dockerfile.hardened .
docker run -d -p 8080:8080 --env-file .env \
  --read-only --tmpfs /tmp \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --name todo-hardened \
  todo-app:v2-hardened

# Vérifier
curl http://localhost:8080/health
```

---

## 🔍 Outils et commandes du TP

### Trivy — Scanner de vulnérabilités

```bash
# Scan CVE de l'image vulnérable
trivy image --severity HIGH,CRITICAL todo-app:v1-unsafe

# Scan de l'image sécurisée (doit avoir 0 CVE CRITICAL)
trivy image --severity CRITICAL todo-app:v2-hardened

# Scan des secrets dans l'image
trivy image --scanners secret todo-app:v1-unsafe

# Export JSON
trivy image --format json --output trivy-report.json todo-app:v1-unsafe
```

### Hadolint — Lint du Dockerfile

```bash
hadolint Dockerfile              # Version vulnérable
hadolint Dockerfile.hardened     # Version sécurisée
```

### Dive — Analyse des layers

```bash
dive todo-app:v1-unsafe          # Mode interactif
CI=true dive todo-app:v1-unsafe  # Mode CI
```

### Docker Bench for Security

```bash
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security
sudo ./docker-bench-security.sh -c container_images
```

---

## ❌ Vulnérabilités intentionnelles

| ID | Type | Localisation | Outil de détection |
|---|---|---|---|
| V01 | SQL Injection | `routes.py:login()` | Bandit B608 / Semgrep |
| V02 | SQL Injection | `routes.py:get_tasks()` | Bandit B608 |
| V03 | SQL Injection | `routes.py:search_tasks()` | Bandit B608 |
| V04 | XSS | `routes.py:search_tasks()` + `index.html` | Semgrep / Manuel |
| V05 | OS Command Injection (RCE) | `routes.py:admin_ping()` | Bandit B602 |
| V06 | Path Traversal | `routes.py:read_file()` | Semgrep |
| V07 | IDOR | `routes.py:get_task()` | Manuel |
| V08 | Broken Auth | `routes.py:login()` | Manuel |
| V09 | MD5 Password Hashing | `models.py:set_password()` | Bandit B303 |
| V10 | Hardcoded Secrets | `routes.py`, `Dockerfile` | Gitleaks / Bandit B106 |
| V11 | Image non épinglée | `Dockerfile:FROM python:3.11` | Hadolint DL3006 |
| V12 | Run as root | `Dockerfile` | Hadolint DL3002 / Docker Bench |
| V13 | Debug mode en prod | `Dockerfile:ENV FLASK_DEBUG=1` | Trivy misconfig |
| V14 | CVE dans dépendances | `requirements.txt` | Trivy / Safety |
| V15 | Socket Docker monté | `docker-compose.yml` | Docker Bench |

---

## ✅ Corrections appliquées en Phase 3

| Vulnérabilité | Correction | Fichier |
|---|---|---|
| SQL Injection | Requêtes paramétrées / ORM | `app/routes.py` |
| XSS | Échappement Jinja2 + CSP | `app/templates/` |
| OS Injection | Suppression de l'endpoint | `app/routes.py` |
| MD5 | Migration vers bcrypt/argon2 | `app/models.py` |
| Hardcoded Secrets | Variables d'environnement | `.env` + `docker-compose.hardened.yml` |
| Image root | Utilisateur dédié non-root | `Dockerfile.hardened` |
| Image complète | python:3.11-slim + multi-stage | `Dockerfile.hardened` |
| CVE dépendances | Mises à jour | `requirements-secure.txt` |
| Debug mode | `FLASK_DEBUG=0` | `Dockerfile.hardened` |

---

## 🧪 Lancer les tests

```bash
pip install pytest flask flask-sqlalchemy
pytest tests/ -v
```

---

## 📚 Ressources

- [Trivy Documentation](https://trivy.dev/latest/docs/)
- [Hadolint Rules](https://github.com/hadolint/hadolint/wiki/DL-rules)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [NIST SP 800-190](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

---

## 📄 Licence

Projet pédagogique — Master DevOps. Usage interne uniquement.
