from flask import Flask
from .models import db


def create_app(config=None):
    app = Flask(__name__)

    # Configuration de base
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "super-secret-key-123"  # ❌ Secret hardcodé

    if config:
        app.config.update(config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import api
    app.register_blueprint(api)

    return app
