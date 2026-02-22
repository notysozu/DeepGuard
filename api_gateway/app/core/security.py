"""Compatibility shim.

Security ownership moved to shared.security (OAuth2/JWT).
"""

from shared.security import get_current_user as require_auth

__all__ = ["require_auth"]
