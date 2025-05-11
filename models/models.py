from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    ARRAY,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    created_at = Column(Date, default=datetime.now())
    is_default = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="workspaces")
    models = relationship("ModelEntry", back_populates="workspace")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_default": self.is_default,
            "user_id": self.user_id,
            "models": [model.to_dict() for model in self.models] if self.models else [],
        }


class ModelEntry(Base):
    __tablename__ = "model_entry"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    developer = Column(String(120))
    model_type = Column(String(50))
    status = Column(String(50))
    date_interacted = Column(Date, default=datetime.now())
    tags = Column(ARRAY(String), default=list)
    notes = Column(Text)
    source_links = Column(ARRAY(String), default=list)
    parameters = Column(Integer, nullable=True)
    license = Column(String(50), nullable=True)
    version = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    user = relationship("User", back_populates="models")
    workspace = relationship("Workspace", back_populates="models")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "developer": self.developer,
            "model_type": self.model_type,
            "status": self.status,
            "date_interacted": self.date_interacted.isoformat()
            if self.date_interacted
            else None,
            "tags": self.tags or [],
            "notes": self.notes,
            "source_links": self.source_links or [],
            "parameters": self.parameters,
            "license": self.license,
            "version": self.version,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "username": self.user.username if self.user else None,
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.now())

    models = relationship("ModelEntry", back_populates="user")
    workspaces = relationship("Workspace", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "workspaces": [workspace.to_dict() for workspace in self.workspaces]
            if self.workspaces
            else [],
        }


Base.metadata.create_all(engine)
