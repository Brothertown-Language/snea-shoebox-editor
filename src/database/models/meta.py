from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from sqlalchemy.sql import func
from ..base import Base

class SchemaVersion(Base):
    """
    Tracks the current version of the database schema.
    Used to ensure non-destructive updates and manage migrations.
    """
    __tablename__ = 'schema_version'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False)
    applied_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    description = Column(Text)
