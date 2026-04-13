# CONVENTION: Every new SQLAlchemy model class MUST include __table_args__ with 'extend_existing': True.
# - Simple table (no other constraints): __table_args__ = {'extend_existing': True}
# - Table with constraints (e.g. UniqueConstraint): __table_args__ = (UniqueConstraint(...), {'extend_existing': True})
# This prevents sqlalchemy.exc.InvalidRequestError on Streamlit hot-reload / module re-import.
