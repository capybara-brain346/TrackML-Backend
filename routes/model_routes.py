from flask import Blueprint, request, jsonify
from models.models import ModelEntry, session
from datetime import datetime
from services.model_extractor_service import ModelExtractor
from services.agent_service import AgentService
from services.rag_service import RAGService
from flask_cors import cross_origin


bp = Blueprint("models", __name__, url_prefix="/models")

model_extractor = ModelExtractor()
rag_service = RAGService()


@bp.route("/", methods=["GET"])
@cross_origin()
def get_models():
    models = session.query(ModelEntry).all()
    return jsonify([model.to_dict() for model in models])


@bp.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_model(id):
    model = session.query(ModelEntry).get(id)
    if not model:
        return {"error": "Model not found"}, 404
    return jsonify(model.to_dict())


@bp.route("/", methods=["POST"])
@cross_origin()
def create_model():
    data = request.get_json()
    if "date_interacted" in data and data["date_interacted"]:
        data["date_interacted"] = datetime.fromisoformat(data["date_interacted"]).date()

    model = ModelEntry(**data)
    session.add(model)
    session.commit()
    return jsonify(model.to_dict()), 201


@bp.route("/<int:id>", methods=["PUT"])
@cross_origin()
def update_model(id):
    model = session.query(ModelEntry).get(id)
    if not model:
        return {"error": "Model not found"}, 404

    data = request.get_json()
    if "date_interacted" in data and data["date_interacted"]:
        data["date_interacted"] = datetime.fromisoformat(data["date_interacted"]).date()

    for key, value in data.items():
        setattr(model, key, value)

    session.commit()
    return jsonify(model.to_dict())


@bp.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_model(id):
    model = session.query(ModelEntry).get(id)
    if not model:
        return {"error": "Model not found"}, 404

    session.delete(model)
    session.commit()
    return "", 204


@bp.route("/search", methods=["GET"])
@cross_origin()
def search_models():
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

    return jsonify([model.to_dict() for model in models.all()])


@bp.route("/autofill", methods=["POST"])
@cross_origin()
def autofill_model():
    data = request.get_json()
    model_id: str = data.get("model_id")
    model_links: list = data.get("model_links")

    agent_service = AgentService(model_id=model_id, model_links=model_links)
    agent_response = agent_service.run_agent()
    return jsonify(agent_response)


@bp.route("/<int:id>/insights", methods=["GET"])
@cross_origin()
def get_model_insights(id):
    model = session.query(ModelEntry).get(id)
    if not model:
        return {"error": "Model not found"}, 404

    insights = rag_service.generate_model_insights(model.to_dict())
    return jsonify(insights)


@bp.route("/insights/compare", methods=["POST"])
@cross_origin()
def compare_models():
    data = request.get_json()
    model_ids = data.get("model_ids", [])

    if not model_ids:
        return {"error": "No model IDs provided"}, 400

    models = session.query(ModelEntry).filter(ModelEntry.id.in_(model_ids)).all()
    if not models:
        return {"error": "No models found"}, 404

    analysis = rag_service.analyze_multiple_models(
        [model.to_dict() for model in models]
    )
    return jsonify(analysis)
