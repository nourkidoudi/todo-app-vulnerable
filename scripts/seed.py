#!/usr/bin/env python3
"""
seed.py — Initialiser la base de données avec des données de test
Usage : python scripts/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User, Task


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Création des données de test...")

        # Supprimer les données existantes
        db.drop_all()
        db.create_all()

        # Créer des utilisateurs
        alice = User(username="alice", email="alice@example.com", role="admin")
        alice.set_password("password123")

        bob = User(username="bob", email="bob@example.com", role="user")
        bob.set_password("password456")

        charlie = User(username="charlie", email="charlie@example.com", role="user")
        charlie.set_password("password789")

        db.session.add_all([alice, bob, charlie])
        db.session.commit()
        print(f"  ✅ 3 utilisateurs créés (alice, bob, charlie)")

        # Créer des tâches
        tasks = [
            Task(title="Installer Docker", description="Télécharger et installer Docker Desktop", priority="high", user_id=alice.id),
            Task(title="Lire le TP DevSecOps", description="Prendre connaissance de l énoncé", priority="high", user_id=alice.id, completed=True),
            Task(title="Scanner l image avec Trivy", description="trivy image todo-app:v1-unsafe", priority="high", user_id=alice.id),
            Task(title="Auditer le Dockerfile", description="hadolint Dockerfile", priority="medium", user_id=bob.id),
            Task(title="Corriger les injections SQL", description="Utiliser des requêtes paramétrées", priority="high", user_id=bob.id),
            Task(title="Migrer MD5 vers bcrypt", description="requirements-secure.txt", priority="medium", user_id=bob.id),
            Task(title="Externaliser les secrets", description="Créer le fichier .env", priority="high", user_id=charlie.id),
            Task(title="Durcir le Dockerfile", description="Multi-stage build + non-root", priority="medium", user_id=charlie.id),
            Task(title="Configurer le pipeline CI/CD", description=".github/workflows/docker-security.yml", priority="low", user_id=charlie.id),
            Task(title="Rédiger le rapport final", description="Tableau comparatif avant/après", priority="low", user_id=alice.id),
        ]

        db.session.add_all(tasks)
        db.session.commit()
        print(f"  ✅ {len(tasks)} tâches créées")

        print("\n📋 Résumé :")
        print(f"  Utilisateurs : {User.query.count()}")
        print(f"  Tâches       : {Task.query.count()}")
        print(f"  Complétées   : {Task.query.filter_by(completed=True).count()}")
        print("\n🚀 L application est prête ! Accédez à http://localhost:5000")


if __name__ == "__main__":
    seed()
