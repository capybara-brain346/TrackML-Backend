from typing import Dict, Any, Optional
from models.models import User, session
from sqlalchemy.orm.session import Session as SQLAlchemySession
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class AuthService:
    def __init__(self, db_session: SQLAlchemySession = session):
        self.session = db_session
        self.secret_key = os.getenv("JWT_SECRET_KEY", "default-secret-key")

    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        if self.session.query(User).filter_by(username=username).first():
            return {"error": "Username already exists"}

        if self.session.query(User).filter_by(email=email).first():
            return {"error": "Email already exists"}

        user = User(username=username, email=email)
        user.set_password(password)

        self.session.add(user)
        self.session.commit()

        return {"message": "User registered successfully", "user": user.to_dict()}

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        user = self.session.query(User).filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"error": "Invalid username or password"}

        token = self.generate_token(user)
        return {"token": token, "user": user.to_dict()}

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        user = self.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}

        for key, value in data.items():
            if key == "password":
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)

        self.session.commit()
        return {"message": "User updated successfully", "user": user.to_dict()}

    def generate_token(self, user: User) -> str:
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(days=1),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user = self.get_user_by_id(payload["user_id"])
            if not user:
                return {"error": "User not found"}
            return {"user": user.to_dict()}
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> Dict[str, Any]:
        user = self.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}

        if not user.check_password(old_password):
            return {"error": "Invalid current password"}

        user.set_password(new_password)
        self.session.commit()
        return {"message": "Password changed successfully"}
