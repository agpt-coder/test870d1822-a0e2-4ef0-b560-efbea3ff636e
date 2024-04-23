from prisma import Client
from pydantic import BaseModel


class Role(BaseModel):
    """
    An enum representing available user roles within the system.
    """

    pass


class User(BaseModel):
    """
    A simplified user model showing publicly safe details.
    """

    id: str
    email: str
    role: Role
    avatar_url: str


class UpdateUserResponse(BaseModel):
    """
    Confirms the successful update of the user's profile and returns the updated information.
    """

    success: bool
    updated_user_details: User


async def update_user(
    id: str, email: str, password: str, role: Role, avatar_url: str
) -> UpdateUserResponse:
    """
    Updates an existing user's profile information in the database.

    Args:
        id (str): The unique identifier for the user, used to locate the profile to update.
        email (str): The new email address for the user. Must be valid and unique.
        password (str): The new password for the user. Password should have strong validation rules prior to this step.
        role (Role): The new role for the user, allowing for permission changes within an enum set.
        avatar_url (str): A new URL for the user's avatar image.

    Returns:
        UpdateUserResponse: An object that indicates whether the update was successful along with the updated user details.
    """
    prisma_client = Client()
    updated_user = await prisma_client.user.update(
        where={"id": id},
        data={
            "email": email,
            "password": password,
            "role": role,
            "avatarUrl": avatar_url,
        },
    )
    return UpdateUserResponse(success=True, updated_user_details=updated_user)
