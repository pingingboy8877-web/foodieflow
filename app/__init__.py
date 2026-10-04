import os
from flask import Flask
from app.database import init_db

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
    app.config["JSON_SORT_KEYS"] = False

    init_db()

    from app.routes import bp
    app.register_blueprint(bp)
    return app
