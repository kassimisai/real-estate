from sqlalchemy import Column, String, UUID, JSON
from .base import Base, TimestampMixin
import uuid

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    license_number = Column(String)
    settings = Column(JSON, default={})
