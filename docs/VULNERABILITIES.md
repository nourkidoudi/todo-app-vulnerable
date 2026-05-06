# 📖 Guide des Vulnérabilités — Todo App TP DevSecOps

Ce document liste et explique chaque vulnérabilité intentionnelle de l'application.
À utiliser comme **guide de référence** pendant la Phase 2 du TP.

---

## V01 — SQL Injection dans `/api/login`

**Fichier :** `app/routes.py` — fonction `login()`

**Code vulnérable :**
```python
raw_sql = f"SELECT * FROM users WHERE username='{username}' AND role='user'"
result = db.session.execute(db.text(raw_sql))
```

**Exploitation :**
```
username = admin' --
```
→ La requête devient : `SELECT * FROM users WHERE username='admin' --' AND role='user'`
→ Le commentaire `--` neutralise la vérification du rôle.

**Correction Phase 3 :** Utiliser `User.query.filter_by(username=username).first()`

---

## V05 — OS Command Injection (RCE) dans `/api/admin/ping`

**Fichier :** `app/routes.py` — fonction `admin_ping()`

**Code vulnérable :**
```python
cmd = f"ping -c 1 {host}"
output = subprocess.check_output(cmd, shell=True)
```

**Exploitation :**
```
GET /api/admin/ping?host=localhost; cat /etc/passwd
GET /api/admin/ping?host=localhost; ls -la /app
```

**Correction Phase 3 :** Supprimer cet endpoint ou utiliser `subprocess.run(["ping", "-c", "1", host], shell=False)`

---

## V06 — Path Traversal dans `/api/files`

**Fichier :** `app/routes.py` — fonction `read_file()`

**Code vulnérable :**
```python
filepath = os.path.join("/app/data", filename)
with open(filepath, "r") as f:
    content = f.read()
```

**Exploitation :**
```
GET /api/files?name=../../../etc/passwd
GET /api/files?name=../routes.py
```

**Correction Phase 3 :**
```python
import os
safe_base = os.path.realpath("/app/data")
requested = os.path.realpath(os.path.join(safe_base, filename))
if not requested.startswith(safe_base):
    return jsonify({"error": "Forbidden"}), 403
```

---

## V09 — Hashage MD5 des mots de passe

**Fichier :** `app/models.py` — méthode `set_password()`

**Code vulnérable :**
```python
self.password = hashlib.md5(password.encode()).hexdigest()
```

**Problèmes :**
1. MD5 est trop rapide (milliards de hashes/seconde sur GPU)
2. Pas de salt → vulnérable aux rainbow tables
3. Hash MD5 exposé dans l'API (`to_dict()`)

**Correction Phase 3 :**
```python
from bcrypt import hashpw, gensalt
self.password = hashpw(password.encode('utf-8'), gensalt(rounds=12))
```

---

## V10 — Secrets hardcodés

**Fichiers :** `app/routes.py`, `Dockerfile`

**Code vulnérable :**
```python
JWT_SECRET = "jwt-secret-hardcoded-do-not-use"
ADMIN_API_KEY = "admin-key-12345"
```

```dockerfile
ENV SECRET_KEY="hardcoded-secret-key-do-not-use-123"
```

**Correction Phase 3 :**
```python
import os
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET non définie")
```

---

## V12 — Exécution en tant que root

**Fichier :** `Dockerfile`

**Problème :** Aucune directive `USER` → le processus tourne en root.

**Vérification :**
```bash
docker exec todo-unsafe whoami
# root
```

**Correction Phase 3 :** `Dockerfile.hardened` avec `USER appuser`

---

*Pour chaque vulnérabilité : utilisez les outils du TP (Bandit, Semgrep, Trivy, Gitleaks) pour la détecter, puis appliquez la correction de la Phase 3.*
