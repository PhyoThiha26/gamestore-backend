from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from config import Config
import pymysql
pymysql.converters.encoders[str] = lambda s: s.encode("utf-8")
pymysql.converters.decoders["UTF8"] = lambda b: b.decode("utf-8")

db = SQLAlchemy()

migrate = Migrate()

def create_app():

    app = Flask(__name__)


    app.config.from_object(Config)

    import cloudinary

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

    CORS(app)

    db.init_app(app)

    migrate.init_app(app,db)

    from app.models import User,Game,Listing

    with app.app_context():
        db.create_all()

    from app.routes.auth_routes import auth
    app.register_blueprint(auth)

    from app.routes.admin_routes import admin

    app.register_blueprint(admin)

    from app.routes.main_routes import main

    app.register_blueprint(main)

    from app.routes.api_routes import api

    app.register_blueprint(api)

    

    return app
