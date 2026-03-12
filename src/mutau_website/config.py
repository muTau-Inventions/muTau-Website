"""
Config loader — reads config.yml from CONFIG_PATH env var or project root.
DATABASE_URL and SECRET_KEY intentionally stay as env vars (Docker secrets).
"""
import os
import logging

try:
    import yaml
except ImportError as exc:
    raise ImportError("PyYAML is required: add 'pyyaml' to requirements.txt") from exc

logger = logging.getLogger(__name__)

_CONFIG_PATH_ENV = "CONFIG_PATH"
_DEFAULT_PATHS = [
    os.environ.get(_CONFIG_PATH_ENV, ""),
    "/app/config.yml",                                                      # container default
    os.path.join(os.path.dirname(__file__), "..", "..", "config.yml"),      # repo root (dev)
]


def _load() -> dict:
    for path in _DEFAULT_PATHS:
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            logger.info("Loaded config from %s", os.path.abspath(path))
            return data

    logger.warning(
        "config.yml not found (searched: %s). Using empty defaults.",
        [p for p in _DEFAULT_PATHS if p],
    )
    return {}


cfg: dict = _load()


# ── Convenience accessors ──────────────────────────────────────────────────

def get_log_level() -> int:
    name = cfg.get("app", {}).get("log_level", "INFO").upper()
    return getattr(logging, name, logging.INFO)


def get_mail_cfg() -> dict:
    return cfg.get("mail", {})


def get_base_url() -> str:
    """
    Base URL used to build absolute links in emails.
    Configured via app.base_url in config.yml.
    Falls back to http://localhost if not set.
    """
    return cfg.get("app", {}).get("base_url", "http://localhost").rstrip("/")