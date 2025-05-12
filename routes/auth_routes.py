import os
from flask import Blueprint, request, jsonify
from models.models import User, session
from flask_cors import cross_origin, CORS
import jwt
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.typing import ApiResponseHandler
from utils.logging import logger

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

bp = Blueprint("auth", __name__, url_prefix="/auth")
CORS(
    bp,
    resources={
        r"/*": {
            "origins": [FRONTEND_URL],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)

SECRET_KEY = os.getenv("SECRET_KEY")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Request missing authorization token")
            return jsonify(ApiResponseHandler.error("Token is missing", 401)), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = session.query(User).get(data["user_id"])
            if not current_user:
                logger.warning(
                    f"Invalid token used - user not found for ID: {data.get('user_id')}"
                )
                return jsonify(ApiResponseHandler.error("Invalid token", 401)), 401
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return jsonify(ApiResponseHandler.error("Invalid token", 401)), 401
        return f(current_user, *args, **kwargs)

    return decorated


@bp.route("/register", methods=["POST", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["POST", "OPTIONS"])
def register_user():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    logger.info(f"New user registration attempt for username: {data.get('username')}")

    if not all(k in data for k in ["username", "email", "password"]):
        logger.warning("Registration attempt with missing required fields")
        return jsonify(ApiResponseHandler.error("Missing required fields", 400)), 400

    if session.query(User).filter_by(username=data["username"]).first():
        logger.warning(
            f"Registration failed - username already exists: {data['username']}"
        )
        return jsonify(ApiResponseHandler.error("Username already exists", 400)), 400

    if session.query(User).filter_by(email=data["email"]).first():
        logger.warning(f"Registration failed - email already exists: {data['email']}")
        return jsonify(ApiResponseHandler.error("Email already exists", 400)), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    try:
        session.add(user)
        session.commit()
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(days=1)},
            SECRET_KEY,
            algorithm="HS256",
        )
        logger.info(f"User successfully registered: {user.username}")
        return jsonify(
            ApiResponseHandler.success(
                {"token": token, "user": user.to_dict()}, status_code=201
            )
        ), 201
    except Exception as e:
        session.rollback()
        logger.error(f"Registration failed due to error: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    logger.info(f"Login attempt for email: {data.get('email')}")

    if not all(k in data for k in ["email", "password"]):
        logger.warning("Login attempt with missing required fields")
        return jsonify(ApiResponseHandler.error("Missing required fields", 400)), 400

    user = session.query(User).filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        logger.warning(f"Failed login attempt for email: {data.get('email')}")
        return jsonify(ApiResponseHandler.error("Invalid credentials", 401)), 401

    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.utcnow() + timedelta(days=1)},
        SECRET_KEY,
        algorithm="HS256",
    )
    logger.info(f"Successful login for user: {user.username}")
    return jsonify(
        ApiResponseHandler.success({"token": token, "user": user.to_dict()})
    ), 200


@bp.route("/verify-token", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
@token_required
def verify_token(current_user):
    logger.debug(f"Token verification successful for user: {current_user.username}")
    return jsonify(ApiResponseHandler.success({"user": current_user.to_dict()})), 200


@bp.route("/user/<int:user_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["PUT", "OPTIONS"])
@token_required
def update_user(current_user, user_id):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"User update requested for ID: {user_id}")
    data = request.get_json()
    user = session.query(User).get(user_id)

    if not user:
        logger.warning(f"Update failed - user not found: {user_id}")
        return jsonify(ApiResponseHandler.error("User not found", 404)), 404

    try:
        if "username" in data:
            existing_user = (
                session.query(User).filter_by(username=data["username"]).first()
            )
            if existing_user and existing_user.id != user_id:
                logger.warning(f"Username already taken: {data['username']}")
                return jsonify(
                    ApiResponseHandler.error("Username already exists", 400)
                ), 400
            user.username = data["username"]

        if "email" in data:
            existing_user = session.query(User).filter_by(email=data["email"]).first()
            if existing_user and existing_user.id != user_id:
                logger.warning(f"Email already taken: {data['email']}")
                return jsonify(
                    ApiResponseHandler.error("Email already exists", 400)
                ), 400
            user.email = data["email"]

        if "password" in data:
            user.set_password(data["password"])

        if "is_active" in data:
            user.is_active = data["is_active"]

        session.commit()
        logger.info(f"User {user_id} successfully updated")
        return jsonify(ApiResponseHandler.success(user.to_dict())), 200

    except Exception as e:
        session.rollback()
        logger.error(f"User update failed due to error: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/user/<int:user_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["DELETE", "OPTIONS"])
@token_required
def delete_user(current_user, user_id):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"User deactivation requested for ID: {user_id}")
    user = session.query(User).get(user_id)

    if not user:
        logger.warning(f"Deactivation failed - user not found: {user_id}")
        return jsonify(ApiResponseHandler.error("User not found", 404)), 404

    try:
        user.is_active = False
        session.commit()
        logger.info(f"User {user_id} successfully deactivated")
        return jsonify(
            ApiResponseHandler.success({"message": "User deactivated successfully"})
        ), 200

    except Exception as e:
        session.rollback()
        logger.error(f"User deactivation failed due to error: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500
