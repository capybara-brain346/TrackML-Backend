from models.models import User, ModelEntry, Workspace, session
from services.workspace_service import WorkspaceService
from datetime import datetime


def migrate_to_workspaces():
    workspace_service = WorkspaceService(session)

    try:
        # Get all users
        users = session.query(User).all()

        for user in users:
            # Create default workspace for each user
            default_workspace = workspace_service.create_default_workspace(user.id)

            # Get all models for the user
            user_models = session.query(ModelEntry).filter_by(user_id=user.id).all()

            # Move all existing models to the default workspace
            for model in user_models:
                model.workspace_id = default_workspace.id

            session.commit()

        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
        return False


if __name__ == "__main__":
    migrate_to_workspaces()
