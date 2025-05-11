from typing import Dict, Any, List, Optional
from models.models import ModelEntry, User, session
from sqlalchemy.orm.session import Session as SQLAlchemySession
from datetime import datetime
from services.workspace_service import WorkspaceService


class ModelService:
    def __init__(self, db_session: SQLAlchemySession = session):
        self.session = db_session
        self.workspace_service = WorkspaceService(db_session)

    def create_model(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = data.get("workspace_id")
        if not workspace_id:
            default_workspace = self.workspace_service.get_or_create_default_workspace(
                user_id
            )
            workspace_id = default_workspace.id

        model = ModelEntry(
            name=data["name"],
            developer=data.get("developer"),
            model_type=data.get("model_type"),
            status=data.get("status", "active"),
            tags=data.get("tags", []),
            notes=data.get("notes"),
            source_links=data.get("source_links", []),
            parameters=data.get("parameters"),
            license=data.get("license"),
            version=data.get("version"),
            user_id=user_id,
            workspace_id=workspace_id,
            date_interacted=datetime.now(),
        )

        self.session.add(model)
        self.session.commit()
        return model.to_dict()

    def get_model(self, model_id: int, user_id: int) -> Optional[ModelEntry]:
        return (
            self.session.query(ModelEntry)
            .filter_by(id=model_id, user_id=user_id)
            .first()
        )

    def get_user_models(
        self, user_id: int, workspace_id: Optional[int] = None
    ) -> List[ModelEntry]:
        query = self.session.query(ModelEntry).filter_by(user_id=user_id)
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        return query.all()

    def update_model(
        self, model_id: int, user_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        model = self.get_model(model_id, user_id)
        if not model:
            return {"error": "Model not found"}

        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        model.date_interacted = datetime.now()
        self.session.commit()
        return model.to_dict()

    def delete_model(self, model_id: int, user_id: int) -> bool:
        model = self.get_model(model_id, user_id)
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def update_model_tags(
        self, model_id: int, user_id: int, tags: List[str]
    ) -> Dict[str, Any]:
        model = self.get_model(model_id, user_id)
        if not model:
            return {"error": "Model not found"}

        model.tags = tags
        model.date_interacted = datetime.now()
        self.session.commit()
        return model.to_dict()

    def search_models(
        self,
        user_id: int,
        query: str = None,
        model_type: str = None,
        workspace_id: int = None,
        tags: List[str] = None,
    ) -> List[ModelEntry]:
        base_query = self.session.query(ModelEntry).filter_by(user_id=user_id)

        if workspace_id:
            base_query = base_query.filter_by(workspace_id=workspace_id)

        if query:
            base_query = base_query.filter(
                ModelEntry.name.ilike(f"%{query}%")
                | ModelEntry.developer.ilike(f"%{query}%")
                | ModelEntry.notes.ilike(f"%{query}%")
            )

        if model_type:
            base_query = base_query.filter_by(model_type=model_type)

        if tags:
            for tag in tags:
                base_query = base_query.filter(ModelEntry.tags.contains([tag]))

        return base_query.all()

    def get_model_types(self, user_id: int) -> List[str]:
        return [
            r[0]
            for r in self.session.query(ModelEntry.model_type)
            .filter_by(user_id=user_id)
            .distinct()
            .all()
        ]

    def get_all_tags(self, user_id: int) -> List[str]:
        models = self.get_user_models(user_id)
        tags = set()
        for model in models:
            if model.tags:
                tags.update(model.tags)
        return list(tags)

    def bulk_update_workspace(
        self, user_id: int, model_ids: List[int], target_workspace_id: int
    ) -> Dict[str, Any]:
        models = (
            self.session.query(ModelEntry)
            .filter(ModelEntry.id.in_(model_ids), ModelEntry.user_id == user_id)
            .all()
        )

        if not models:
            return {"error": "No models found"}

        workspace = self.workspace_service.get_workspace(target_workspace_id, user_id)
        if not workspace:
            return {"error": "Target workspace not found"}

        for model in models:
            model.workspace_id = target_workspace_id
            model.date_interacted = datetime.now()

        self.session.commit()
        return {"message": f"Successfully moved {len(models)} models to workspace"}
