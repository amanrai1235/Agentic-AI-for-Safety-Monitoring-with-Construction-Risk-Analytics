"""Time helpers.

The database stores naive UTC timestamps, so every module goes through utcnow()
instead of the deprecated utcnow().
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
