from datetime import datetime
from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class EmojiActivity(BaseModel):
    """
    Represents a single emoji interpretation activity with essential details.
    """

    emojiChar: str
    meaning: str
    timestamp: datetime


class UserActivityResponse(BaseModel):
    """
    Describes the response structure for a user's activity, including a list of their past emoji interpretation requests.
    """

    activities: List[EmojiActivity]


async def get_user_activity() -> UserActivityResponse:
    """
    Retrieves the user's past emoji interpretation requests.

    This function queries the EmojiQuery model for the current user's past emoji searches,
    transforming the data into a structured response of their activity.

    Returns:
        UserActivityResponse: Describes the response structure for a user's activity, including a list of their past emoji interpretation requests.

    Example:
        Assuming the User 'John Doe' has interpreted emojis, calling get_user_activity for John Doe
        might return UserActivityResponse with a list of EmojiActivity objects.
    """
    current_user_id = "some-user-id"
    emoji_queries = await prisma.models.EmojiQuery.prisma().find_many(
        where={"UserId": current_user_id}, include={"Emoji": True}
    )
    activities = [
        EmojiActivity(
            emojiChar=query.Emoji.emojiChar,
            meaning=query.Emoji.meaning,
            timestamp=query.createdAt,
        )
        for query in emoji_queries
    ]
    return UserActivityResponse(activities=activities)
