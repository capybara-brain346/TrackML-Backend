from flask import Flask
from flask_cors import CORS
from backend.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    from backend.routes.routes import bp as models_bp

    app.register_blueprint(models_bp, url_prefix="/api/v1")

    return app
