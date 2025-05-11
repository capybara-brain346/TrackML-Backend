from models.models import Base, engine
from config import Config
from flask import Flask, request, make_response
from flask_cors import CORS


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={
            r"/api/v1/*": {
                "origins": ["https://trackml-frontend.onrender.com"],
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
            response.headers.add(
                "Access-Control-Allow-Origin", "https://trackml-frontend.onrender.com"
            )
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

    app.register_blueprint(models_bp, url_prefix="/api/v1/models")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    return app


app = create_app()
Base.metadata.create_all(engine)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
