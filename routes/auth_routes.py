from flask import Blueprint, request, jsonify
from models.models import User, session
from flask_cors import cross_origin, CORS

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


@bp.route("/register", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["POST", "OPTIONS"])
def register_user():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    if not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    if session.query(User).filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    if session.query(User).filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    try:
        session.add(user)
        session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    if not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    user = session.query(User).filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify(user.to_dict()), 200


@bp.route("/user/<int:user_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["PUT", "OPTIONS"])
def update_user(user_id):
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    user = session.query(User).get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        if "username" in data:
            existing_user = (
                session.query(User).filter_by(username=data["username"]).first()
            )
            if existing_user and existing_user.id != user_id:
                return jsonify({"error": "Username already exists"}), 400
            user.username = data["username"]

        if "email" in data:
            existing_user = session.query(User).filter_by(email=data["email"]).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({"error": "Email already exists"}), 400
            user.email = data["email"]

        if "password" in data:
            user.set_password(data["password"])

        if "is_active" in data:
            user.is_active = data["is_active"]

        session.commit()
        return jsonify(user.to_dict()), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/user/<int:user_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["DELETE", "OPTIONS"])
def delete_user(user_id):
    if request.method == "OPTIONS":
        return "", 200

    user = session.query(User).get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        user.is_active = False
        session.commit()
        return jsonify({"message": "User deactivated successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
