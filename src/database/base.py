"""
Shared base for all database models to avoid circular imports.

AI Agent Instructions:
- Source of truth for database schema: docs/database/DATABASE_SPECIFICATION.md
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
