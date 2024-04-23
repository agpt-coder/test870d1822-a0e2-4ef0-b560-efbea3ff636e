import prisma
import prisma.models
from fastapi import HTTPException
from pydantic import BaseModel


class LogoutResponse(BaseModel):
    """
    This model confirms the successful invalidation and logout process of a user. It provides a simple success message.
    """

    message: str


async def logout_user(auth_token: str) -> LogoutResponse:
    """
    Logs out a user, invalidating their access token.

    This function searches for an ApiKey record matching the provided auth_token. If found, it deletes the ApiKey from the database,
    effectively invalidating the session token. If no matching ApiKey is found, this means the token is already invalid or never
    existed, and an exception is raised.

    Args:
    auth_token (str): An authentication token unique to the user's session, provided via request headers. In a real-world scenario,
    the token is not passed as a body or path parameter but extracted from the headers.

    Returns:
    LogoutResponse: This model confirms the successful invalidation and logout process of a user. It provides a simple success message.

    Raises:
    HTTPException: If no ApiKey is found with the provided auth_token, indicating the token is invalid or doesn't exist.
    """
    api_key = await prisma.models.ApiKey.prisma().find_unique(where={"key": auth_token})
    if api_key:
        await prisma.models.ApiKey.prisma().delete(where={"id": api_key.id})
        return LogoutResponse(message="User logged out successfully.")
    else:
        raise HTTPException(
            status_code=404, detail="Authentication token is invalid or not found."
        )
