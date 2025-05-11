import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models.models import ModelEntry, session
from datetime import datetime
from services.agent_service import AgentService
from services.model_insights_service import ModelInsightsService
from services.semantic_search_service import SemanticSearchService
from flask_cors import cross_origin, CORS
from api_typing.typing import ApiResponseHandler
from routes.auth_routes import token_required
from services.model_service import ModelService
from typing import Dict, Any

bp = Blueprint("models", __name__, url_prefix="/models")
CORS(
    bp,
    resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)

model_insights_service = ModelInsightsService()
semantic_search_service = SemanticSearchService()
model_service = ModelService()


@bp.route("/models", methods=["POST"])
@token_required
def create_model(current_user: Dict[str, Any]):
    data = request.get_json()
    if not data.get("name"):
        return jsonify(
            ApiResponseHandler.error(message="Model name is required", status_code=400)
        ), 400

    result = model_service.create_model(current_user["id"], data)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=400)
        ), 400

    return jsonify(
        ApiResponseHandler.success(
            data=result, message="Model created successfully", status_code=201
        )
    ), 201


@bp.route("/models", methods=["GET"])
@token_required
def get_models(current_user: Dict[str, Any]):
    workspace_id = request.args.get("workspace_id", type=int)
    query = request.args.get("query")
    model_type = request.args.get("model_type")
    tags = request.args.getlist("tags")

    models = model_service.search_models(
        user_id=current_user["id"],
        query=query,
        model_type=model_type,
        workspace_id=workspace_id,
        tags=tags,
    )
    return jsonify(
        ApiResponseHandler.success(
            data=[model.to_dict() for model in models],
            message="Models retrieved successfully",
        )
    )


@bp.route("/models/<int:model_id>", methods=["GET"])
@token_required
def get_model(current_user: Dict[str, Any], model_id: int):
    model = model_service.get_model(model_id, current_user["id"])
    if not model:
        return jsonify(
            ApiResponseHandler.error(message="Model not found", status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(
            data=model.to_dict(), message="Model retrieved successfully"
        )
    )


@bp.route("/models/<int:model_id>", methods=["PUT"])
@token_required
def update_model(current_user: Dict[str, Any], model_id: int):
    data = request.get_json()
    result = model_service.update_model(model_id, current_user["id"], data)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(data=result, message="Model updated successfully")
    )


@bp.route("/models/<int:model_id>", methods=["DELETE"])
@token_required
def delete_model(current_user: Dict[str, Any], model_id: int):
    success = model_service.delete_model(model_id, current_user["id"])
    if not success:
        return jsonify(
            ApiResponseHandler.error(message="Model not found", status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(message="Model deleted successfully")
    ), 204


@bp.route("/models/<int:model_id>/tags", methods=["PUT"])
@token_required
def update_tags(current_user: Dict[str, Any], model_id: int):
    data = request.get_json()
    tags = data.get("tags", [])
    result = model_service.update_model_tags(model_id, current_user["id"], tags)
    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(data=result, message="Tags updated successfully")
    )


@bp.route("/models/types", methods=["GET"])
@token_required
def get_model_types(current_user: Dict[str, Any]):
    types = model_service.get_model_types(current_user["id"])
    return jsonify(
        ApiResponseHandler.success(
            data=types, message="Model types retrieved successfully"
        )
    )


@bp.route("/models/tags", methods=["GET"])
@token_required
def get_all_tags(current_user: Dict[str, Any]):
    tags = model_service.get_all_tags(current_user["id"])
    return jsonify(
        ApiResponseHandler.success(data=tags, message="Tags retrieved successfully")
    )


@bp.route("/models/bulk-workspace-update", methods=["POST"])
@token_required
def bulk_update_workspace(current_user: Dict[str, Any]):
    data = request.get_json()
    model_ids = data.get("model_ids", [])
    target_workspace_id = data.get("target_workspace_id")

    if not model_ids or not target_workspace_id:
        return jsonify(
            ApiResponseHandler.error(
                message="Missing required parameters", status_code=400
            )
        ), 400

    result = model_service.bulk_update_workspace(
        current_user["id"], model_ids, target_workspace_id
    )

    if "error" in result:
        return jsonify(
            ApiResponseHandler.error(message=result["error"], status_code=400)
        ), 400
    return jsonify(ApiResponseHandler.success(message=result["message"]))
