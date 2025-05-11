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


@bp.route("/", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["GET", "OPTIONS"])
def get_models():
    if request.method == "OPTIONS":
        return "", 200
    models = session.query(ModelEntry).all()
    return jsonify(ApiResponseHandler.success([model.to_dict() for model in models]))


@bp.route("/<int:id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["GET", "OPTIONS"])
def get_model(id):
    if request.method == "OPTIONS":
        return "", 200
    model = session.query(ModelEntry).get(id)
    if not model:
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404
    return jsonify(ApiResponseHandler.success(model.to_dict()))


@bp.route("/", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["POST", "OPTIONS"])
def create_model():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    if "date_interacted" in data and data["date_interacted"]:
        data["date_interacted"] = datetime.fromisoformat(data["date_interacted"]).date()

    model = ModelEntry(**data)
    session.add(model)
    session.commit()
    return jsonify(ApiResponseHandler.success(model.to_dict(), status_code=201)), 201


@bp.route("/<int:id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["PUT", "OPTIONS"])
def update_model(id):
    if request.method == "OPTIONS":
        return "", 200
    model = session.query(ModelEntry).get(id)
    if not model:
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    data = request.get_json()
    if "date_interacted" in data and data["date_interacted"]:
        data["date_interacted"] = datetime.fromisoformat(data["date_interacted"]).date()

    for key, value in data.items():
        setattr(model, key, value)

    session.commit()
    return jsonify(ApiResponseHandler.success(model.to_dict()))


@bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["DELETE", "OPTIONS"])
def delete_model(id):
    if request.method == "OPTIONS":
        return "", 200
    model = session.query(ModelEntry).get(id)
    if not model:
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    session.delete(model)
    session.commit()
    return jsonify(
        ApiResponseHandler.success(
            None, message="Model deleted successfully", status_code=204
        )
    ), 204


@bp.route("/search", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["GET", "OPTIONS"])
def search_models():
    if request.method == "OPTIONS":
        return "", 200
    query = request.args.get("q", "")
    model_type = request.args.get("type")
    status = request.args.get("status")
    tag = request.args.get("tag")

    models = session.query(ModelEntry)

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
@cross_origin(origins=["http://localhost:5173"], methods=["POST", "OPTIONS"])
def autofill_model():
    if request.method == "OPTIONS":
        return "", 200

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

        agent_service = AgentService(
            model_id=model_id, model_links=model_links, doc_paths=file_paths
        )
        agent_response = agent_service.run_agent()

        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception:
                pass

        return jsonify(ApiResponseHandler.success({"response": agent_response})), 200
    except Exception as e:
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception:
                pass
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500


@bp.route("/<int:id>/insights", methods=["GET", "POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["GET", "POST", "OPTIONS"])
def get_model_insights(id):
    if request.method == "OPTIONS":
        return "", 200

    model = session.query(ModelEntry).get(id)
    if not model:
        return jsonify(ApiResponseHandler.error("Model not found", 404)), 404

    insights = model_insights_service.generate_model_insights(model.to_dict())
    return jsonify(ApiResponseHandler.success(insights))


@bp.route("/insights/compare", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["POST", "OPTIONS"])
def compare_models():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    model_ids = data.get("model_ids", [])
    custom_prompt = data.get("prompt")

    if not model_ids:
        return jsonify(ApiResponseHandler.error("No model IDs provided", 400)), 400

    models = session.query(ModelEntry).filter(ModelEntry.id.in_(model_ids)).all()
    if not models:
        return jsonify(ApiResponseHandler.error("No models found", 404)), 404

    analysis = model_insights_service.analyze_multiple_models(
        [model.to_dict() for model in models], custom_prompt
    )
    return jsonify(ApiResponseHandler.success(analysis))


@bp.route("/semantic-search", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], methods=["GET", "OPTIONS"])
def semantic_search():
    if request.method == "OPTIONS":
        return "", 200

    query = request.args.get("q", "")
    if not query:
        return jsonify(ApiResponseHandler.error("Search query is required", 400)), 400

    try:
        results = semantic_search_service.search(query)
        return jsonify(ApiResponseHandler.success(results))
    except Exception as e:
        return jsonify(ApiResponseHandler.error(str(e), 500)), 500
