# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
API key service — credential lifecycle for the agent-facing API (issue #1420).

Follows the EventLogService pattern: static methods, optional session
injection, error-safe writes. Secret discipline (spec R-6):

- Secrets are generated with the stdlib ``secrets`` module (``token_urlsafe(32)``
  = 256 bits of entropy).
- Secrets are stored ONLY as PBKDF2-HMAC-SHA256 hashes — per-secret random
  salt, 600,000 iterations (OWASP guidance), versioned string format
  ``pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>``.
- The plaintext secret is returned exactly once by ``create_key`` /
  ``regenerate_secret`` for one-time display and is NEVER persisted, logged,
  or embedded in audit events.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import secrets as _secrets
from datetime import UTC, datetime

from src.database.connection import get_session
from src.database.models.api_keys import ApiKeys
from src.logging_config import get_logger
from src.services.event_log_service import EventLogService

logger = get_logger("snea.api_key_service")

_PBKDF2_ITERATIONS = 600_000
_KEY_PREFIX = "snea_"

# Audit event types (spec R-7)
EVENT_CREATED = "api_key_created"
EVENT_REGENERATED = "api_key_regenerated"
EVENT_ENABLED = "api_key_enabled"
EVENT_DISABLED = "api_key_disabled"
EVENT_REVOKED = "api_key_revoked"


def hash_secret(plaintext_secret: str, *, iterations: int = _PBKDF2_ITERATIONS) -> str:
    """Hash a plaintext secret into the versioned PBKDF2 string format."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", plaintext_secret.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(dk).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"


def verify_secret(plaintext_secret: str, stored_hash: str) -> bool:
    """Constant-time verification of a plaintext secret against a stored hash.

    Returns False for any malformed stored hash (never raises) so a corrupt
    row fails closed as an invalid credential.
    """
    try:
        scheme, iterations_s, salt_b64, hash_b64 = stored_hash.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iterations_s)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
    except (ValueError, TypeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", plaintext_secret.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


class ApiKeyService:
    """Create, rotate, enable/disable, revoke, and verify API key pairs."""

    # ── Lifecycle ─────────────────────────────────────────────────────

    @staticmethod
    def create_key(label: str, created_by: str, session=None) -> tuple[str, str]:
        """Create a key pair. Returns ``(key, plaintext_secret)`` — the secret
        is shown exactly once by the caller and never persisted."""
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            key = _KEY_PREFIX + _secrets.token_urlsafe(16)
            plaintext_secret = _secrets.token_urlsafe(32)
            row = ApiKeys(
                key=key,
                secret_hash=hash_secret(plaintext_secret),
                label=label,
                created_by=created_by,
                enabled=True,
            )
            session.add(row)
            if not _provided:
                session.commit()
            _audit(
                EVENT_CREATED,
                f"API key created: {key}",
                {"key": key, "label": label, "acting_admin": created_by},
                session,
                not _provided,
            )
            return key, plaintext_secret
        except Exception:
            if not _provided:
                try:
                    session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass

    @staticmethod
    def regenerate_secret(key: str, acting_admin: str, session=None) -> str | None:
        """Replace the stored hash; the old secret is invalid immediately.

        Returns the new plaintext secret (displayed exactly once) or None if
        the key is unknown or revoked.
        """
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            row = session.query(ApiKeys).filter(ApiKeys.key == key).one_or_none()
            if row is None or row.revoked_at is not None:
                if not _provided:
                    session.rollback()
                return None
            plaintext_secret = _secrets.token_urlsafe(32)
            row.secret_hash = hash_secret(plaintext_secret)
            if not _provided:
                session.commit()
            _audit(
                EVENT_REGENERATED,
                f"API key secret regenerated: {key}",
                {"key": key, "acting_admin": acting_admin},
                session,
                not _provided,
            )
            return plaintext_secret
        except Exception:
            if not _provided:
                try:
                    session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass

    @staticmethod
    def set_enabled(key: str, enabled: bool, acting_admin: str, session=None) -> bool:
        """Enable or disable a key. Returns False for unknown/revoked keys."""
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            row = session.query(ApiKeys).filter(ApiKeys.key == key).one_or_none()
            if row is None or row.revoked_at is not None:
                if not _provided:
                    session.rollback()
                return False
            row.enabled = enabled
            if not _provided:
                session.commit()
            event_type = EVENT_ENABLED if enabled else EVENT_DISABLED
            _audit(
                event_type,
                f"API key {'enabled' if enabled else 'disabled'}: {key}",
                {"key": key, "acting_admin": acting_admin},
                session,
                not _provided,
            )
            return True
        except Exception:
            if not _provided:
                try:
                    session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass

    @staticmethod
    def revoke_key(key: str, acting_admin: str, session=None) -> bool:
        """Soft-revoke a key (marks ``revoked_at``; the row is retained for audit)."""
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            row = session.query(ApiKeys).filter(ApiKeys.key == key).one_or_none()
            if row is None or row.revoked_at is not None:
                if not _provided:
                    session.rollback()
                return False
            row.revoked_at = datetime.now(UTC)
            row.enabled = False
            if not _provided:
                session.commit()
            _audit(
                EVENT_REVOKED,
                f"API key revoked: {key}",
                {"key": key, "acting_admin": acting_admin},
                session,
                not _provided,
            )
            return True
        except Exception:
            if not _provided:
                try:
                    session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass

    # ── Verification ──────────────────────────────────────────────────

    @staticmethod
    def authenticate(key: str, secret: str, session=None) -> tuple[str, ApiKeys | None]:
        """Verify a credential pair.

        Returns ``(status, row)`` where status is:

        - ``"ok"``       — valid, enabled, not revoked (row returned;
                           ``last_used_at`` is updated)
        - ``"invalid"``  — unknown key or wrong secret (row is None)
        - ``"inactive"`` — known key that is disabled or revoked

        The API layer maps ``invalid`` to 401 and ``inactive`` to 403 with a
        uniform 401 message that never distinguishes unknown key from bad
        secret.
        """
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            row = session.query(ApiKeys).filter(ApiKeys.key == key).one_or_none()
            if row is None or not verify_secret(secret, row.secret_hash):
                return "invalid", None
            if row.revoked_at is not None or not row.enabled:
                return "inactive", row
            row.last_used_at = datetime.now(UTC)
            if not _provided:
                session.commit()
                # Reload all attributes while still attached: after close() the
                # instance is detached and any expired attribute would raise
                # DetachedInstanceError on access by the caller.
                session.refresh(row)
            return "ok", row
        except Exception:
            if not _provided:
                try:
                    session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass

    # ── Listing ───────────────────────────────────────────────────────

    @staticmethod
    def list_keys(session=None) -> list[ApiKeys]:
        """All key rows (including revoked — retained for audit), newest first."""
        _provided = session is not None
        if not _provided:
            session = get_session()
        try:
            return session.query(ApiKeys).order_by(ApiKeys.id.desc()).all()
        finally:
            if not _provided:
                try:
                    session.close()
                except Exception:
                    pass


def _audit(event_type: str, message: str, details: dict, session, own_session: bool) -> None:
    """Write a lifecycle audit event; failures never interrupt the caller.

    When the service owns the session it must NOT piggyback the event on it:
    the lifecycle commit already happened and ``close()`` would discard the
    uncommitted event — so ``None`` is passed and EventLogService uses its
    own committing session. When the caller provided the session, the event
    rides on it and commits with the caller's transaction.
    """
    EventLogService.log_event(
        event_type=event_type,
        severity="info",
        message=message,
        source="src.services.api_key_service",
        details=details,
        session=None if own_session else session,
    )
