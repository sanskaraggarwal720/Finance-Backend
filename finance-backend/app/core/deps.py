from fastapi import Header, HTTPException, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User, Role


def get_current_user(x_user_id: int = Header(..., description="ID of the acting user"), session: Session = Depends(get_session)) -> User:
    """
    Mock authentication: caller passes their user ID via X-User-Id header.
    In production this would be a JWT or session token.
    """
    user = session.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive.")
    return user


def require_role(*roles: Role):
    """Factory that returns a dependency enforcing one of the given roles."""
    def check(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role(s): {[r.value for r in roles]}."
            )
        return current_user
    return check


# Convenience aliases
require_viewer_or_above = require_role(Role.viewer, Role.analyst, Role.admin)
require_analyst_or_above = require_role(Role.analyst, Role.admin)
require_admin = require_role(Role.admin)
