from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, ARRAY, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://piyush:root123@localhost:5432/trackml"
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


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
        }


Base.metadata.create_all(engine)
