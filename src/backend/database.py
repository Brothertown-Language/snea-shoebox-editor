# Copyright (c) 2026 Brothertown Language
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
import streamlit as st

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    citation_format = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    records = relationship("Record", back_populates="source")

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    lx = Column(String, nullable=False)
    ps = Column(String)
    ge = Column(String)
    mdf_data = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='draft')
    source_page = Column(String)
    current_version = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String)
    reviewed_at = Column(TIMESTAMP(timezone=True))
    reviewed_by = Column(String)
    
    source = relationship("Source", back_populates="records")
    history = relationship("EditHistory", back_populates="record")

class EditHistory(Base):
    __tablename__ = 'edit_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('records.id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, nullable=False)
    prev_data = Column(Text)
    current_data = Column(Text, nullable=False)
    user_id = Column(String, nullable=False)
    change_summary = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    record = relationship("Record", back_populates="history")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    github_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    name = Column(String)
    last_login = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class UserActivityLog(Base):
    __tablename__ = 'user_activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='CASCADE'))
    github_org = Column(String, nullable=False)
    github_team = Column(String)
    role = Column(String, nullable=False, default='viewer')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

def get_db_url():
    """Get database URL from Streamlit secrets or environment variables."""
    try:
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            return st.secrets["connections"]["postgresql"]["url"]
    except Exception:
        pass
    return os.getenv("DATABASE_URL")

def init_db():
    """Initialize the database schema."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get a new database session."""
    db_url = get_db_url()
    if not db_url:
        raise ValueError("Database URL not found in secrets or environment.")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
