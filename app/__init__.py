from flask import Flask
from flask_cors import CORS
from .db import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = 'your_secret_key'

    init_db()

    from .routes.main_routes import main
    from .routes.admin_routes import admin

    app.register_blueprint(main)
    app.register_blueprint(admin)

    return app