# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
ApiKeys model — credentials for the agent-facing read-only API (issue #1420).

A key+secret pair issued through the admin view. The secret is stored ONLY
as a PBKDF2-HMAC-SHA256 hash (versioned string format) — the plaintext
secret is displayed exactly once at issuance and never persisted. Rows are
retained after revocation (soft mark via ``revoked_at``) for audit.
"""

from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.sql import func

from src.database.base import Base


class ApiKeys(Base):
    """A single API credential pair for the agent-facing records API."""

    __tablename__ = "api_keys"
    __table_args__ = {"extend_existing": True}  # Required: prevents re-import errors on Streamlit hot-reload

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)  # public identifier: 'snea_' + token_urlsafe(16)
    secret_hash = Column(String, nullable=False)  # pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    label = Column(String)  # human-readable label set by the issuing admin
    created_by = Column(String)  # identity of the acting admin
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    enabled = Column(Boolean, nullable=False, server_default="true")
    revoked_at = Column(TIMESTAMP(timezone=True))  # soft revoke; rows retained for audit
    last_used_at = Column(TIMESTAMP(timezone=True))  # updated on successful authentication
