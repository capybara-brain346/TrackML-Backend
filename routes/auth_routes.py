import os
from flask import Blueprint, request, jsonify
from models.models import User, session
from flask_cors import cross_origin, CORS
import jwt
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
from api_typing.typing import ApiResponseHandler
from services.auth_service import AuthService
from typing import Dict, Any

load_dotenv()

bp = Blueprint("auth", __name__, url_prefix="/auth")
CORS(
    bp,
    resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)

SECRET_KEY = os.getenv("SECRET_KEY")
auth_service = AuthService()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify(
                ApiResponseHandler.error(message="Token is missing", status_code=401)
            ), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = session.query(User).get(data["user_id"])
            if not current_user:
                return jsonify(
                    ApiResponseHandler.error(message="Invalid token", status_code=401)
                ), 401
        except:
            return jsonify(
                ApiResponseHandler.error(message="Invalid token", status_code=401)
            ), 401
        return f(current_user, *args, **kwargs)

    return decorated


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify(
            ApiResponseHandler.error(message="Missing required fields", status_code=400)
        ), 400

    result = auth_service.register_user(username, email, password)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=400)
        ), 400

    return jsonify(
        ApiResponseHandler.success(
            data=result["user"], message=result["message"], status_code=201
        )
    ), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify(
            ApiResponseHandler.error(message="Missing required fields", status_code=400)
        ), 400

    result = auth_service.login_user(email, password)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=401)
        ), 401

    return jsonify(
        ApiResponseHandler.success(
            data={"token": result["token"], "user": result["user"]},
            message="Login successful",
        )
    )


@bp.route("/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify(
            ApiResponseHandler.error(message="Token is required", status_code=400)
        ), 400

    result = auth_service.verify_token(token)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=401)
        ), 401

    return jsonify(
        ApiResponseHandler.success(
            data=result["user"], message="Token verified successfully"
        )
    )


@bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json()
    user_id = data.get("user_id")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not all([user_id, old_password, new_password]):
        return jsonify(
            ApiResponseHandler.error(message="Missing required fields", status_code=400)
        ), 400

    result = auth_service.change_password(user_id, old_password, new_password)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=400)
        ), 400

    return jsonify(ApiResponseHandler.success(message=result["message"]))


@bp.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    data = request.get_json()
    result = auth_service.update_user(user_id, data)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=400)
        ), 400

    return jsonify(
        ApiResponseHandler.success(data=result["user"], message=result["message"])
    )


@bp.route("/user/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, user_id):
    user = session.query(User).get(user_id)

    if not user:
        return jsonify(
            ApiResponseHandler.error(message="User not found", status_code=404)
        ), 404

    try:
        user.is_active = False
        session.commit()
        return jsonify(
            ApiResponseHandler.success(message="User deactivated successfully")
        )
    except Exception as e:
        session.rollback()
        return jsonify(ApiResponseHandler.error(message=str(e), status_code=500)), 500
