# Copyright (c) 2026 Brothertown Language
"""
Shared base for all database models to avoid circular imports.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
