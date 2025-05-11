from typing import List, Optional, Dict, Any
from models.models import Workspace, ModelEntry, User, session
from sqlalchemy.orm.session import Session as SQLAlchemySession
from datetime import datetime


class WorkspaceService:
    def __init__(self, db_session: SQLAlchemySession = session):
        self.session = db_session

    def create_workspace(
        self, user_id: int, name: str, description: str = None
    ) -> Workspace:
        workspace = Workspace(
            name=name,
            description=description,
            user_id=user_id,
            created_at=datetime.now(),
        )
        self.session.add(workspace)
        self.session.commit()
        return workspace

    def get_user_workspaces(self, user_id: int) -> List[Workspace]:
        return self.session.query(Workspace).filter_by(user_id=user_id).all()

    def get_workspace(self, workspace_id: int, user_id: int) -> Optional[Workspace]:
        return (
            self.session.query(Workspace)
            .filter_by(id=workspace_id, user_id=user_id)
            .first()
        )

    def update_workspace(
        self, workspace_id: int, user_id: int, data: Dict[str, Any]
    ) -> Optional[Workspace]:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        for key, value in data.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        self.session.commit()
        return workspace

    def delete_workspace(self, workspace_id: int, user_id: int) -> bool:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return False

        if workspace.is_default:
            return False

        self.session.delete(workspace)
        self.session.commit()
        return True

    def add_model_to_workspace(
        self, workspace_id: int, model_id: int, user_id: int
    ) -> bool:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return False

        model = (
            self.session.query(ModelEntry)
            .filter_by(id=model_id, user_id=user_id)
            .first()
        )
        if not model:
            return False

        model.workspace_id = workspace_id
        self.session.commit()
        return True

    def move_model_between_workspaces(
        self,
        model_id: int,
        source_workspace_id: int,
        target_workspace_id: int,
        user_id: int,
    ) -> bool:
        model = (
            self.session.query(ModelEntry)
            .filter_by(id=model_id, user_id=user_id, workspace_id=source_workspace_id)
            .first()
        )

        target_workspace = self.get_workspace(target_workspace_id, user_id)

        if not model or not target_workspace:
            return False

        model.workspace_id = target_workspace_id
        self.session.commit()
        return True

    def get_workspace_models(self, workspace_id: int, user_id: int) -> List[ModelEntry]:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return []

        return (
            self.session.query(ModelEntry)
            .filter_by(workspace_id=workspace_id, user_id=user_id)
            .all()
        )

    def create_default_workspace(self, user_id: int) -> Workspace:
        default_workspace = Workspace(
            name="Default Workspace",
            description="Your default workspace",
            user_id=user_id,
            is_default=True,
            created_at=datetime.now(),
        )
        self.session.add(default_workspace)
        self.session.commit()
        return default_workspace

    def get_or_create_default_workspace(self, user_id: int) -> Workspace:
        default_workspace = (
            self.session.query(Workspace)
            .filter_by(user_id=user_id, is_default=True)
            .first()
        )

        if not default_workspace:
            default_workspace = self.create_default_workspace(user_id)

        return default_workspace
