import os
import subprocess
from flask import Blueprint, request, jsonify, render_template, session
from .models import db, User, Task

api = Blueprint("api", __name__)

# ============================================================
# ❌ CONFIG VULNÉRABLE — À corriger en Phase 3
# ============================================================
# Clé JWT hardcodée dans le code source
JWT_SECRET = "jwt-secret-hardcoded-do-not-use"
# Clé API admin exposée
ADMIN_API_KEY = "admin-key-12345"
# ============================================================


# ── HEALTH CHECK ────────────────────────────────────────────
@api.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


# ── PAGE PRINCIPALE ─────────────────────────────────────────
@api.route("/")
def index():
    return render_template("index.html")


# ── AUTHENTIFICATION ────────────────────────────────────────

@api.route("/api/register", methods=["POST"])
def register():
    """❌ Aucune validation des entrées"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email", "")

    # ❌ Pas de vérification si les champs sont vides
    # ❌ Pas de vérification de la longueur du mot de passe
    # ❌ Pas de validation du format email

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # ❌ Retourne le hash MD5 du mot de passe dans la réponse
    return jsonify({"message": "User created", "user": user.to_dict()}), 201


@api.route("/api/login", methods=["POST"])
def login():
    """❌ Pas de protection contre le bruteforce"""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # ❌ Injection SQL par concaténation directe
    raw_sql = f"SELECT * FROM users WHERE username='{username}' AND role='user'"

    try:
        result = db.session.execute(db.text(raw_sql))
        row = result.fetchone()
    except Exception as e:
        # ❌ Stack trace retournée à l'utilisateur
        return jsonify({"error": str(e), "query": raw_sql}), 500

    if row is None:
        return jsonify({"error": "Invalid credentials"}), 401

    # Vérification du mot de passe (faible car MD5)
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session["username"] = user.username
    # ❌ Token JWT avec secret hardcodé, sans expiration
    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "token": JWT_SECRET,  # ❌ Retourne le secret directement !
    }), 200


# ── TÂCHES ──────────────────────────────────────────────────

@api.route("/api/tasks", methods=["GET"])
def get_tasks():
    """❌ Pas d'authentification requise — toutes les tâches sont publiques"""
    # ❌ IDOR : n'importe qui peut voir les tâches de tous les utilisateurs
    user_id = request.args.get("user_id")

    if user_id:
        # ❌ Injection SQL dans le paramètre user_id
        raw_sql = f"SELECT * FROM tasks WHERE user_id = {user_id}"
        try:
            result = db.session.execute(db.text(raw_sql))
            tasks = [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            return jsonify({"error": str(e), "query": raw_sql}), 500
    else:
        tasks = [t.to_dict() for t in Task.query.all()]

    return jsonify({"tasks": tasks, "count": len(tasks)}), 200


@api.route("/api/tasks", methods=["POST"])
def create_task():
    """❌ Pas de validation ni de sanitisation des entrées"""
    data = request.get_json()

    # ❌ Pas d'authentification
    # ❌ Pas de validation des champs obligatoires
    task = Task(
        title=data.get("title", ""),          # ❌ Peut être vide
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        due_date=data.get("due_date"),
        user_id=data.get("user_id", 1),       # ❌ user_id fourni par le client
    )

    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created", "task": task.to_dict()}), 201


@api.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """❌ Pas de vérification que l'utilisateur est propriétaire de la tâche (IDOR)"""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict()), 200


@api.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """❌ N'importe qui peut modifier n'importe quelle tâche"""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "completed" in data:
        task.completed = data["completed"]
    if "priority" in data:
        task.priority = data["priority"]

    db.session.commit()
    return jsonify({"message": "Task updated", "task": task.to_dict()}), 200


@api.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """❌ N'importe qui peut supprimer n'importe quelle tâche"""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


# ── RECHERCHE VULNÉRABLE ────────────────────────────────────

@api.route("/api/search", methods=["GET"])
def search_tasks():
    """❌ Double injection : SQL + XSS via réponse HTML non échappée"""
    query = request.args.get("q", "")

    # ❌ Injection SQL directe dans la clause LIKE
    raw_sql = f"SELECT * FROM tasks WHERE title LIKE '%{query}%' OR description LIKE '%{query}%'"
    try:
        result = db.session.execute(db.text(raw_sql))
        tasks = [dict(row._mapping) for row in result.fetchall()]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # ❌ Réponse HTML avec contenu non échappé → XSS
    html = f"<h1>Résultats pour : {query}</h1>"
    html += f"<p>{len(tasks)} tâche(s) trouvée(s)</p>"
    for t in tasks:
        html += f"<div><b>{t.get('title', '')}</b> - {t.get('description', '')}</div>"

    return html, 200, {"Content-Type": "text/html"}


# ── ENDPOINT ADMIN DANGEREUX ────────────────────────────────

@api.route("/api/admin/users", methods=["GET"])
def list_users():
    """❌ Endpoint admin sans authentification forte — clé en dur"""
    api_key = request.headers.get("X-API-Key", "")
    # ❌ Clé API hardcodée et vérification par comparaison simple
    if api_key != ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    # ❌ Retourne les hashes MD5 des mots de passe de tous les utilisateurs
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@api.route("/api/admin/ping", methods=["GET"])
def admin_ping():
    """❌ Injection de commandes OS via le paramètre host"""
    host = request.args.get("host", "localhost")

    # ❌ COMMANDE OS INJECTÉE DIRECTEMENT — Remote Code Execution
    cmd = f"ping -c 1 {host}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({"output": output.decode()}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output.decode()}), 500


# ── FICHIERS ────────────────────────────────────────────────

@api.route("/api/files", methods=["GET"])
def read_file():
    """❌ Path traversal — lecture de fichiers arbitraires sur le serveur"""
    filename = request.args.get("name", "readme.txt")

    # ❌ Aucune validation du chemin — path traversal possible
    # Exemple d'attaque : /api/files?name=../../../etc/passwd
    filepath = os.path.join("/app/data", filename)
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content}), 200
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filepath}"}), 404
    except Exception as e:
        # ❌ Erreur verbosité maximale — expose le chemin complet
        return jsonify({"error": str(e), "path": filepath}), 500


# ── STATS ───────────────────────────────────────────────────

@api.route("/api/stats", methods=["GET"])
def get_stats():
    """Endpoint de statistiques — pas de vulnérabilité intentionnelle ici"""
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(completed=True).count()
    total_users = User.query.count()
    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "total_users": total_users,
    }), 200
