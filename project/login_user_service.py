import hashlib
import os
from datetime import datetime, timedelta

import prisma
import prisma.models
from pydantic import BaseModel


class LoginUserResponse(BaseModel):
    """
    Upon successful authentication, this model contains the OAuth 2.0 access token along with a message indicating success.
    """

    access_token: str
    token_type: str
    expires_in: int
    message: str


async def login_user(email: str, password: str) -> LoginUserResponse:
    """
    Authenticates a user and returns an access token.

    Args:
    email (str): The email address associated with the user's account.
    password (str): The password for the user's account.

    Returns:
    LoginUserResponse: Upon successful authentication, this model contains the OAuth 2.0 access token along with a message indicating success.

    Example:
    Access token returned upon successful login:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY78...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "message": "Authentication successful."
    }
    """
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = await prisma.models.User.prisma().find_unique(
        where={"email": email, "password": hashed_password}
    )
    if user is not None:
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
        dummy_token = hashlib.md5((user.email + SECRET_KEY).encode("utf-8")).hexdigest()
        expires_in = 3600
        access_token_expiration = datetime.now() + timedelta(seconds=expires_in)
        return LoginUserResponse(
            access_token=dummy_token,
            token_type="Bearer",
            expires_in=expires_in,
            message="Authentication successful.",
        )
    else:
        raise ValueError("Invalid email or password")
