from fastapi import Depends, HTTPException, status

from app.core.oauth2 import get_current_user


def require_role(required_role: str):

    def role_checker(
        current_user=Depends(get_current_user),
    ):
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )

        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return current_user

    return role_checker