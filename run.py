from models.models import Base, engine
from config import Config
from flask import Flask
from flask_cors import CORS


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    from routes.model_routes import bp as models_bp

    app.register_blueprint(models_bp, url_prefix="/api/v1")

    from routes.auth_routes import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)
