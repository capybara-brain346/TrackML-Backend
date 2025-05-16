import os
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin, CORS
from utils.typing import ApiResponseHandler
from dotenv import load_dotenv
from utils.logging import logger

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

bp = Blueprint("health", __name__)
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


@bp.route("/", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
def check_health():
    logger.info(f"Health check requested from IP: {request.remote_addr}")
    return jsonify(
        ApiResponseHandler.success({"status": "healthy", "status_code": 200})
    ), 200
