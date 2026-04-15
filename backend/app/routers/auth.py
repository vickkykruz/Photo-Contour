"""
    Authentication API endpoints.

    Provides routes for user registration, login, token refresh,
    and retrieval of the currently authenticated user.
"""


from fastapi import APIRouter, Depends
from app.core.deps import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def read_me(current_user: dict = Depends(get_current_user)):
    """
    Return basic info about the currently authenticated user.
    Decoded from Firebase ID token.
    """
    return {
        "uid":   current_user.get("uid"),
        "email": current_user.get("email"),
    }