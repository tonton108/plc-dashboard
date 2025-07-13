from flask import Flask
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from backend.db import db

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # ✅ モデルとルートをここでインポート
    from backend.db import models
    from backend.api.routes import register_routes
    register_routes(app)

    print(f"✅ Registered tables: {db.Model.metadata.tables.keys()}")
    print(f"✅ URL Map:\n{app.url_map}")


    return app

def periodic_log_fetch():
    print("📡 periodic_log_fetch started (dummy)")

def wait_for_db(session):
    import time
    while True:
        try:
            session.execute("SELECT 1")
            break
        except Exception:
            time.sleep(1)
            print("Waiting for DB...")

__all__ = ["create_app", "db", "periodic_log_fetch", "wait_for_db"]
