# Copyright (c) 2026 Brothertown Language
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

class User(Base):
    """
    User identity and metadata linked to GitHub authentication.
    Uses email as the primary logical identifier for cross-session audit trails.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)  # Primary logic key
    username = Column(String, unique=True, nullable=False)  # GitHub handle
    github_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String)  # Real name for attribution
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    extra_metadata = Column(JSONB)  # Settings/Info
    
    edit_history = relationship("EditHistory", back_populates="user")
    activity_logs = relationship("UserActivityLog", back_populates="user")
    matchup_entries = relationship("MatchupQueue", back_populates="user")

class UserActivityLog(Base):
    """
    General security and usage audit log.
    Tracks logins, sync sessions, and critical administrative actions.
    """
    __tablename__ = 'user_activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    session_id = Column(String)  # Unique UUID linking activity to a specific edit batch
    action = Column(String, nullable=False)  # e.g., 'login', 'sync_start', 'batch_rollback'
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="activity_logs")

class Permission(Base):
    """
    Access control mapping between GitHub Teams and application roles.
    Defines who can view or edit specific sources.
    
    ROLE ENFORCEMENT:
    - 'admin': Automatic full access to all resources and administrative functions.
    - 'editor': Access to edit, update, and manage MDF records ONLY.
    - 'viewer': Read-only access to records. MAY NEVER edit or modify any data (HARD BLOCK).
    """
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='RESTRICT'))  # NULL = all
    github_org = Column(String, nullable=False)
    github_team = Column(String, nullable=False)  # Mandatory: No NULL teams allowed for security
    role = Column(String, nullable=False, default='viewer')  # 'admin', 'editor', 'viewer'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
