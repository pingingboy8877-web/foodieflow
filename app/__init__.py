from flask import Flask
from app.database import init_db

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = 'super-secret-jwt-key-foodie-flow-2026'

    # Initialize SQL Database Tables
    init_db()

    from app.routes import bp
    app.register_blueprint(bp)

    return app
