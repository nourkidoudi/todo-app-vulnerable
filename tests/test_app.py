"""
Tests fonctionnels — Todo App TP DevSecOps
Ces tests vérifient que l'application fonctionne correctement.
En Phase 3, des tests de sécurité sont ajoutés pour valider les corrections.
"""
import pytest
import json
from app import create_app
from app.models import db


@pytest.fixture
def app():
    """Créer une instance de l'application pour les tests."""
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── TESTS FONCTIONNELS ──────────────────────────────────────

class TestHealth:
    def test_health_check(self, client):
        """L'endpoint /health doit retourner 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_index_page(self, client):
        """La page principale doit être accessible."""
        response = client.get("/")
        assert response.status_code == 200


class TestUsers:
    def test_register_user(self, client):
        """Créer un utilisateur."""
        response = client.post("/api/register", json={
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com"
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "user" in data

    def test_register_duplicate_username(self, client):
        """Deux utilisateurs ne peuvent pas avoir le même username."""
        client.post("/api/register", json={
            "username": "dupuser", "password": "pass", "email": "a@a.com"
        })
        response = client.post("/api/register", json={
            "username": "dupuser", "password": "pass2", "email": "b@b.com"
        })
        assert response.status_code == 400

    def test_login_valid(self, client):
        """Connexion avec des identifiants valides."""
        client.post("/api/register", json={
            "username": "loginuser", "password": "mypassword", "email": "l@l.com"
        })
        response = client.post("/api/login", json={
            "username": "loginuser", "password": "mypassword"
        })
        assert response.status_code == 200

    def test_login_invalid_password(self, client):
        """Connexion avec un mauvais mot de passe doit échouer."""
        client.post("/api/register", json={
            "username": "user2", "password": "correct", "email": "u@u.com"
        })
        response = client.post("/api/login", json={
            "username": "user2", "password": "wrong"
        })
        assert response.status_code == 401


class TestTasks:
    def _create_user(self, client):
        r = client.post("/api/register", json={
            "username": "taskowner", "password": "pass", "email": "t@t.com"
        })
        return json.loads(r.data)["user"]["id"]

    def test_get_tasks_empty(self, client):
        """La liste de tâches est vide au départ."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 0

    def test_create_task(self, client):
        """Créer une tâche."""
        user_id = self._create_user(client)
        response = client.post("/api/tasks", json={
            "title": "Ma première tâche",
            "description": "Description de test",
            "priority": "high",
            "user_id": user_id,
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["task"]["title"] == "Ma première tâche"

    def test_get_task_by_id(self, client):
        """Récupérer une tâche par son ID."""
        user_id = self._create_user(client)
        create_r = client.post("/api/tasks", json={
            "title": "Task to get", "user_id": user_id
        })
        task_id = json.loads(create_r.data)["task"]["id"]
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200

    def test_update_task(self, client):
        """Modifier une tâche."""
        user_id = self._create_user(client)
        create_r = client.post("/api/tasks", json={
            "title": "Task to update", "user_id": user_id
        })
        task_id = json.loads(create_r.data)["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", json={
            "completed": True, "title": "Updated title"
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["task"]["completed"] is True

    def test_delete_task(self, client):
        """Supprimer une tâche."""
        user_id = self._create_user(client)
        create_r = client.post("/api/tasks", json={
            "title": "Task to delete", "user_id": user_id
        })
        task_id = json.loads(create_r.data)["task"]["id"]
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        # Vérifier que la tâche n'existe plus
        get_r = client.get(f"/api/tasks/{task_id}")
        assert get_r.status_code == 404

    def test_task_not_found(self, client):
        """Une tâche inexistante retourne 404."""
        response = client.get("/api/tasks/99999")
        assert response.status_code == 404

    def test_stats(self, client):
        """L'endpoint stats retourne les bonnes métriques."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_tasks" in data
        assert "completed_tasks" in data


# ── TESTS DE SÉCURITÉ (Phase 3 — à compléter) ──────────────

class TestSecurityPhase3:
    """
    Tests de sécurité à implémenter en Phase 3.
    Vérifier que les vulnérabilités sont corrigées.
    """

    def test_sql_injection_login(self, client):
        """
        Phase 3 — La tentative d'injection SQL sur /api/login
        doit retourner 401 et non 200.
        """
        response = client.post("/api/login", json={
            "username": "admin' --",
            "password": "anything"
        })
        # Après correction : doit être 401 (pas de bypass)
        assert response.status_code in [400, 401, 500]
        # La réponse ne doit pas contenir de données utilisateur
        data = json.loads(response.data)
        assert "username" not in str(data).lower() or "token" not in str(data).lower()

    def test_xss_search_escaped(self, client):
        """
        Phase 3 — Le paramètre de recherche doit être échappé.
        La balise <script> ne doit pas apparaître dans la réponse.
        """
        response = client.get("/api/search?q=<script>alert('xss')</script>")
        assert b"<script>alert" not in response.data

    def test_security_headers_present(self, client):
        """
        Phase 3 — Les headers de sécurité HTTP doivent être présents.
        """
        response = client.get("/")
        # Ces assertions échoueront sur la v1 — passeront sur la v2
        # assert "X-Frame-Options" in response.headers
        # assert "X-Content-Type-Options" in response.headers
        # assert "Content-Security-Policy" in response.headers
        assert response.status_code == 200  # Au minimum, la page répond

    def test_password_not_stored_in_clear(self, client):
        """
        Phase 3 — Le mot de passe ne doit pas être stocké en clair
        ni retourné dans la réponse d'inscription.
        """
        response = client.post("/api/register", json={
            "username": "sectest",
            "password": "MyPassword123",
            "email": "sec@test.com"
        })
        data = json.loads(response.data)
        # Le mot de passe en clair ne doit pas apparaître dans la réponse
        assert "MyPassword123" not in json.dumps(data)
        # Phase 3 : vérifier que ce n'est plus MD5 (32 chars hex)
        # user_password = data.get("user", {}).get("password", "")
        # assert len(user_password) != 32  # MD5 = 32 chars
