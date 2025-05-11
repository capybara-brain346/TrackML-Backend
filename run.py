from models.models import Base, engine
from config import Config
from flask import Flask, request, make_response
from flask_cors import CORS
from routes.workspace_routes import workspace_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={
            r"/api/v1/*": {
                "origins": ["http://localhost:5173"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
            }
        },
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
            )
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response

    from routes.model_routes import bp as models_bp
    from routes.auth_routes import bp as auth_bp

    app.register_blueprint(models_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(workspace_bp, url_prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=5000, debug=True)
