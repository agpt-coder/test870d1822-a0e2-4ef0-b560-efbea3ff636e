import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class Role(BaseModel):
    """
    An enum representing available user roles within the system.
    """

    pass


class UserRegistrationResponse(BaseModel):
    """
    Response model confirming the successful registration of a new user.
    """

    user_id: str
    email: str
    role: Role
    message: str


async def create_user(
    email: str, password: str, role: Role
) -> UserRegistrationResponse:
    """
    Registers a new user profile.

    Args:
        email (str): The email address for the user. It acts as the unique identifier for user login.
        password (str): The password for the user. This will be hashed before storage for security.
        role (Role): The role assigned to the user upon registration. Defaults to 'USER' if not specified.

    Returns:
        UserRegistrationResponse: Response model confirming the successful registration of a new user.

    """
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = await prisma.models.User.prisma().create(
        data={"email": email, "password": hashed_password.decode("utf-8"), "role": role}
    )
    return UserRegistrationResponse(
        user_id=user.id,
        email=user.email,
        role=user.role,
        message="User successfully registered.",
    )
