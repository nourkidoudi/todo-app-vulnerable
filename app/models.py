import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Modèle utilisateur — ❌ Mots de passe hashés avec MD5 sans salt"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # ❌ MD5 stocké
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship("Task", backref="owner", lazy=True)

    def set_password(self, password):
        # ❌ MD5 sans salt — vulnérable aux rainbow tables
        self.password = hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password == hashlib.md5(password.encode()).hexdigest()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,  # ❌ Hash exposé dans l'API
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Task(db.Model):
    """Modèle tâche"""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default="medium")
    due_date = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "due_date": self.due_date,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
