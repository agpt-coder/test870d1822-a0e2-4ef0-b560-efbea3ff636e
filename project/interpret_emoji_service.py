import httpx
import prisma
import prisma.models
from fastapi import HTTPException
from pydantic import BaseModel


class InterpretEmojiResponse(BaseModel):
    """
    Response model providing the meaning of the requested emoji character.
    """

    emoji: str
    meaning: str
    source: str


async def get_emoji_meaning_from_groq(emoji: str) -> str:
    """
    Fetches the meaning of an emoji from a hypothetical GROQ API.

    Args:
        emoji (str): The unicode emoji character for which the meaning is requested.

    Returns:
        str: The detailed meaning of the emoji character.

    Raises:
        HTTPException: If the GROQ API call fails or no meaning is found for the given emoji.
    """
    GROQ_API_URL = "https://api.groq.com/emoji-meaning"
    params = {"emoji": emoji}
    async with httpx.AsyncClient() as client:
        response = await client.get(GROQ_API_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Emoji meaning not found")
        data = response.json()
        return data.get("meaning", "")


async def check_emoji_in_database(emoji: str) -> str:
    """
    Checks and retrieves the meaning of an emoji from the local database if it exists.

    Args:
        emoji (str): The unicode emoji character for which the meaning is requested.

    Returns:
        str: The detailed meaning of the emoji character if found in the database, otherwise an empty string.
    """
    emoji_record = await prisma.models.Emoji.prisma().find_unique(
        where={"emojiChar": emoji}
    )
    if emoji_record:
        return emoji_record.meaning
    return ""


async def store_emoji_meaning_to_database(emoji: str, meaning: str):
    """
    Stores the emoji and its meaning into the local database.

    Args:
        emoji (str): The unicode emoji character.
        meaning (str): The meaning of the emoji character.
    """
    await prisma.models.Emoji.prisma().upsert(
        where={"emojiChar": emoji},
        data={"emojiChar": emoji, "meaning": meaning, "update": {"meaning": meaning}},
    )


async def interpret_emoji(emoji: str) -> InterpretEmojiResponse:
    """
    Returns the meaning of the input emoji, either by retrieving it from the local database or by querying the GROQ API,
    and subsequently updates or stores the meaning in the database.

    Args:
        emoji (str): The unicode emoji character for which the meaning is requested.

    Returns:
        InterpretEmojiResponse: Response model providing the meaning of the requested emoji character.
    """
    try:
        meaning = await check_emoji_in_database(emoji)
        if meaning:
            source = "cache"
        else:
            meaning = await get_emoji_meaning_from_groq(emoji)
            if not meaning:
                raise HTTPException(status_code=404, detail="Emoji meaning not found")
            source = "GROQ API"
            await store_emoji_meaning_to_database(emoji, meaning)
        return InterpretEmojiResponse(emoji=emoji, meaning=meaning, source=source)
    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=500, detail="Failed to fetch emoji meaning from GROQ API"
        ) from err
