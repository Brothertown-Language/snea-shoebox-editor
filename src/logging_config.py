# Copyright (c) 2026 Brothertown Language
"""
Centralized logging configuration for the SNEA Shoebox Editor.

Uses standard Python logging. Log level is determined by the runtime environment:
- Local development: DEBUG
- Production (Streamlit Cloud): WARNING
"""
import logging
import sys


def _is_production() -> bool:
    """Detect production environment (Streamlit Cloud runs as 'appuser')."""
    try:
        import getpass
        return getpass.getuser() == "appuser"
    except Exception:
        return False


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger configured for the application environment.

    Args:
        name: Logger name, typically __name__ or a service identifier.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Only configure if the logger has no handlers yet (avoid duplicate setup)
    if not logger.handlers:
        level = logging.WARNING if _is_production() else logging.DEBUG
        logger.setLevel(level)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to root logger to avoid duplicate messages
        logger.propagate = False

    return logger
