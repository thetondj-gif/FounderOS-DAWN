"""FounderOS Microsoft Agent Framework orchestration nucleus."""

from .agents import ROLE_SPECS, role_catalog
from .config import Settings

__all__ = ["ROLE_SPECS", "Settings", "role_catalog"]
