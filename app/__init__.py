from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from supabase import create_client, Client
from .config import Config
from .models import db

# Supabase Configuration
SUPABASE_URL = "https://ydlbtcbabebtcajmvoyl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlkbGJ0Y2JhYmVidGNham12b3lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MDY3MjksImV4cCI6MjA0NjM4MjcyOX0.dh9-iGEp9McKCGicE8PJN0DjlppPtUpGUMV2NP60HkM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .routes import main
        app.register_blueprint(main)

    return app
