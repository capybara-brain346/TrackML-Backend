import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models.models import ModelEntry, session
from datetime import datetime
from services.agent_service import AgentService
from services.model_insights_service import ModelInsightsService
from services.semantic_search_service import SemanticSearchService
from flask_cors import cross_origin, CORS
from utils.typing import ApiResponseHandler
from routes.auth_routes import token_required
from dotenv import load_dotenv
from utils.logging import logger

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

bp = Blueprint("models", __name__, url_prefix="/models")
CORS(
    bp,
    resources={
        r"/*": {
            "origins": [FRONTEND_URL],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)

model_insights_service = ModelInsightsService()
semantic_search_service = SemanticSearchService()


@bp.route("/", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
@token_required
def get_models(current_user):
    if request.method == "OPTIONS":
        return "", 200
    logger.info(f"Fetching all models for user: {current_user.username}")
    models = session.query(ModelEntry).all()
    return jsonify(ApiResponseHandler.success([model.to_dict() for model in models]))


@bp.route("/<int:id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
@token_required
def get_model(current_user, id):
    if request.method == "OPTIONS":
        return "", 200
    logger.info(f"Fetching model {id} for user: {current_user.username}")
    model = session.query(ModelEntry).filter_by(id=id, user_id=current_user.id).first()
    if not model:
        logger.warning(f"Model {id} not found for user: {current_user.username}")
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404
    return jsonify(ApiResponseHandler.success(model.to_dict()))


@bp.route("/", methods=["POST", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["POST", "OPTIONS"])
@token_required
def create_model(current_user):
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    logger.info(f"Creating new model for user: {current_user.username}")

    if "date_interacted" in data and data["date_interacted"]:
        data["date_interacted"] = datetime.fromisoformat(data["date_interacted"]).date()

    data["user_id"] = current_user.id
    model = ModelEntry(**data)

    try:
        session.add(model)
        session.commit()
        logger.info(
            f"Successfully created model {model.id} for user: {current_user.username}"
        )
        return jsonify(
            ApiResponseHandler.success(model.to_dict(), status_code=201)
        ), 201
    except Exception as e:
        logger.error(
            f"Failed to create model for user {current_user.username}: {str(e)}"
        )
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/<int:id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["PUT", "OPTIONS"])
@token_required
def update_model(current_user, id):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"Updating model {id} for user: {current_user.username}")
    model = session.query(ModelEntry).filter_by(id=id, user_id=current_user.id).first()

    if not model:
        logger.warning(
            f"Model {id} not found for update - user: {current_user.username}"
        )
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    try:
        data = request.get_json()
        if "date_interacted" in data and data["date_interacted"]:
            data["date_interacted"] = datetime.fromisoformat(
                data["date_interacted"]
            ).date()

        for key, value in data.items():
            setattr(model, key, value)

        session.commit()
        logger.info(
            f"Successfully updated model {id} for user: {current_user.username}"
        )
        return jsonify(ApiResponseHandler.success(model.to_dict()))
    except Exception as e:
        logger.error(
            f"Failed to update model {id} for user {current_user.username}: {str(e)}"
        )
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["DELETE", "OPTIONS"])
@token_required
def delete_model(current_user, id):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"Deleting model {id} for user: {current_user.username}")
    model = session.query(ModelEntry).filter_by(id=id, user_id=current_user.id).first()

    if not model:
        logger.warning(
            f"Model {id} not found for deletion - user: {current_user.username}"
        )
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    try:
        session.delete(model)
        session.commit()
        logger.info(
            f"Successfully deleted model {id} for user: {current_user.username}"
        )
        return jsonify(
            ApiResponseHandler.success(
                None, message="Model deleted successfully", status_code=204
            )
        ), 204
    except Exception as e:
        logger.error(
            f"Failed to delete model {id} for user {current_user.username}: {str(e)}"
        )
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/search", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
@token_required
def search_models(current_user):
    if request.method == "OPTIONS":
        return "", 200

    query = request.args.get("q", "")
    model_type = request.args.get("type")
    status = request.args.get("status")
    tag = request.args.get("tag")

    logger.info(
        f"Searching models for user {current_user.username} with query: {query}"
    )

    models = session.query(ModelEntry).filter_by(user_id=current_user.id)

    if query:
        models = models.filter(ModelEntry.name.ilike(f"%{query}%"))
    if model_type:
        models = models.filter(ModelEntry.model_type == model_type)
    if status:
        models = models.filter(ModelEntry.status == status)
    if tag:
        models = models.filter(ModelEntry.tags.contains([tag]))

    return jsonify(
        ApiResponseHandler.success([model.to_dict() for model in models.all()])
    )


@bp.route("/autofill", methods=["POST", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["POST", "OPTIONS"])
@token_required
def autofill_model(current_user):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"Starting model autofill for user: {current_user.username}")
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    model_id = request.form.get("model_id")
    model_links = request.form.getlist("model_links")
    uploaded_files = request.files.getlist("files")

    file_paths = []
    try:
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                file_paths.append(file_path)
                logger.debug(f"Saved uploaded file: {filename}")

        agent_service = AgentService(
            model_id=model_id, model_links=model_links, doc_paths=file_paths
        )
        agent_response = agent_service.run_agent()
        logger.info(f"Successfully completed autofill for model {model_id}")

        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")

        return jsonify(ApiResponseHandler.success({"response": agent_response})), 200
    except Exception as e:
        logger.error(f"Autofill failed for model {model_id}: {str(e)}")
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(
                    f"Failed to remove temporary file {file_path}: {str(cleanup_error)}"
                )
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/<int:id>/insights", methods=["GET", "POST", "OPTIONS"])
@cross_origin(
    origins=[FRONTEND_URL],
    methods=["GET", "POST", "OPTIONS"],
)
def get_model_insights(id):
    if request.method == "OPTIONS":
        return "", 200

    logger.info(f"Generating insights for model: {id}")
    model = session.query(ModelEntry).get(id)

    if not model:
        logger.warning(f"Model {id} not found for insights generation")
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    try:
        insights = model_insights_service.generate_model_insights(model.to_dict())
        logger.info(f"Successfully generated insights for model {id}")
        return jsonify(ApiResponseHandler.success(insights))
    except Exception as e:
        logger.error(f"Failed to generate insights for model {id}: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/insights/compare", methods=["POST", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["POST", "OPTIONS"])
@token_required
def compare_models(current_user):
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    model_ids = data.get("model_ids", [])
    custom_prompt = data.get("prompt")

    logger.info(f"Comparing models {model_ids} for user: {current_user.username}")

    if not model_ids:
        logger.warning("Model comparison attempted without model IDs")
        return jsonify(ApiResponseHandler.error("No model IDs provided", 400)), 400

    try:
        models = (
            session.query(ModelEntry)
            .filter(ModelEntry.id.in_(model_ids), ModelEntry.user_id == current_user.id)
            .all()
        )
        if not models:
            logger.warning(f"No models found for comparison with IDs: {model_ids}")
            return jsonify(ApiResponseHandler.error("No models found", 404)), 404

        analysis = model_insights_service.analyze_multiple_models(
            [model.to_dict() for model in models], custom_prompt
        )
        logger.info(f"Successfully compared models {model_ids}")
        return jsonify(ApiResponseHandler.success(analysis))
    except Exception as e:
        logger.error(f"Model comparison failed for IDs {model_ids}: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/semantic-search", methods=["GET", "OPTIONS"])
@cross_origin(origins=[FRONTEND_URL], methods=["GET", "OPTIONS"])
def semantic_search():
    if request.method == "OPTIONS":
        return "", 200

    query = request.args.get("q", "")
    logger.info(f"Semantic search requested with query: {query}")

    if not query:
        logger.warning("Semantic search attempted without query")
        return jsonify(ApiResponseHandler.error("Search query is required", 400)), 400

    try:
        results = semantic_search_service.search(query)
        logger.info("Semantic search completed successfully")
        return jsonify(ApiResponseHandler.success(results))
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500
