from flask import Blueprint, request, jsonify
from services.workspace_service import WorkspaceService
from routes.auth_routes import token_required
from typing import Dict, Any
from api_typing.typing import ApiResponseHandler

workspace_bp = Blueprint("workspace", __name__)
workspace_service = WorkspaceService()


@workspace_bp.route("/workspaces", methods=["POST"])
@token_required
def create_workspace(current_user: Dict[str, Any]):
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify(
            ApiResponseHandler.error(
                message="Workspace name is required", status_code=400
            )
        ), 400

    workspace = workspace_service.create_workspace(
        user_id=current_user["id"], name=name, description=description
    )

    return jsonify(
        ApiResponseHandler.success(
            data=workspace.to_dict(),
            message="Workspace created successfully",
            status_code=201,
        )
    ), 201


@workspace_bp.route("/workspaces", methods=["GET"])
@token_required
def get_workspaces(current_user: Dict[str, Any]):
    workspaces = workspace_service.get_user_workspaces(current_user["id"])
    return jsonify(
        ApiResponseHandler.success(
            data=[workspace.to_dict() for workspace in workspaces],
            message="Workspaces retrieved successfully",
        )
    )


@workspace_bp.route("/workspaces/<int:workspace_id>", methods=["GET"])
@token_required
def get_workspace(current_user: Dict[str, Any], workspace_id: int):
    workspace = workspace_service.get_workspace(workspace_id, current_user["id"])
    if not workspace:
        return jsonify(
            ApiResponseHandler.error(message="Workspace not found", status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(
            data=workspace.to_dict(), message="Workspace retrieved successfully"
        )
    )


@workspace_bp.route("/workspaces/<int:workspace_id>", methods=["PUT"])
@token_required
def update_workspace(current_user: Dict[str, Any], workspace_id: int):
    data = request.get_json()
    workspace = workspace_service.update_workspace(
        workspace_id, current_user["id"], data
    )
    if not workspace:
        return jsonify(
            ApiResponseHandler.error(message="Workspace not found", status_code=404)
        ), 404
    return jsonify(
        ApiResponseHandler.success(
            data=workspace.to_dict(), message="Workspace updated successfully"
        )
    )


@workspace_bp.route("/workspaces/<int:workspace_id>", methods=["DELETE"])
@token_required
def delete_workspace(current_user: Dict[str, Any], workspace_id: int):
    success = workspace_service.delete_workspace(workspace_id, current_user["id"])
    if not success:
        return jsonify(
            ApiResponseHandler.error(message="Cannot delete workspace", status_code=400)
        ), 400
    return jsonify(
        ApiResponseHandler.success(message="Workspace deleted successfully")
    ), 204


@workspace_bp.route("/workspaces/<int:workspace_id>/models", methods=["GET"])
@token_required
def get_workspace_models(current_user: Dict[str, Any], workspace_id: int):
    models = workspace_service.get_workspace_models(workspace_id, current_user["id"])
    return jsonify(
        ApiResponseHandler.success(
            data=[model.to_dict() for model in models],
            message="Workspace models retrieved successfully",
        )
    )


@workspace_bp.route(
    "/workspaces/<int:workspace_id>/models/<int:model_id>", methods=["POST"]
)
@token_required
def add_model_to_workspace(
    current_user: Dict[str, Any], workspace_id: int, model_id: int
):
    success = workspace_service.add_model_to_workspace(
        workspace_id, model_id, current_user["id"]
    )
    if not success:
        return jsonify(
            ApiResponseHandler.error(
                message="Failed to add model to workspace", status_code=400
            )
        ), 400
    return jsonify(
        ApiResponseHandler.success(message="Model added to workspace successfully")
    ), 204


@workspace_bp.route("/workspaces/move-model", methods=["POST"])
@token_required
def move_model(current_user: Dict[str, Any]):
    data = request.get_json()
    model_id = data.get("model_id")
    source_workspace_id = data.get("source_workspace_id")
    target_workspace_id = data.get("target_workspace_id")

    if not all([model_id, source_workspace_id, target_workspace_id]):
        return jsonify(
            ApiResponseHandler.error(
                message="Missing required parameters", status_code=400
            )
        ), 400

    success = workspace_service.move_model_between_workspaces(
        model_id, source_workspace_id, target_workspace_id, current_user["id"]
    )

    if not success:
        return jsonify(
            ApiResponseHandler.error(message="Failed to move model", status_code=400)
        ), 400
    return jsonify(ApiResponseHandler.success(message="Model moved successfully")), 204
