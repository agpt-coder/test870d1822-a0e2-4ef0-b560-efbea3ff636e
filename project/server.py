import logging
from contextlib import asynccontextmanager

import project.create_user_service
import project.get_user_activity_service
import project.interpret_emoji_service
import project.login_user_service
import project.logout_user_service
import project.update_user_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="test",
    lifespan=lifespan,
    description="To create an endpoint that connects to GROQ and takes in an emoji as input to explain its meaning, you'll need to complete several steps leveraging the tech stack provided: Python for programming, FastAPI as the API framework, PostgreSQL as the database, and Prisma as the ORM.\n\n1. Setup FastAPI project and integrate Prisma with PostgreSQL for database operations.\n2. Create a model in Prisma to store emoji meanings obtained from the GROQ documentation or an emoji dictionary.\n3. Use the Python `requests` library to connect to the GROQ API endpoint. In the endpoint handler, accept an emoji as input.\n4. Use the GROQ API to query the meaning of the provided emoji by sending a query from FastAPI to GROQ. You might need to format the query according to GROQ's syntax for retrieving the specific emoji meaning.\n5. Process the response from GROQ, extracting the emoji meaning. Ensure error handling is robust to manage cases where an emoji might not be found or the GROQ service is unavailable.\n6. Store or update the emoji meaning in PostgreSQL via Prisma, to cache results and reduce API calls for commonly requested emojis.\n7. Return the emoji’s meaning to the user in a structured response from your FastAPI endpoint.\n\nImportant Considerations:\n- Implement rate limiting and caching to optimize the performance and avoid hitting GROQ service limits.\n- Ensure the emoji input from users is validated to guard against injection attacks or malformed inputs.\n- Review FastAPI’s async capabilities to make non-blocking calls to the GROQ API, improving the endpoint’s responsiveness.\n- Regularly update your emoji database as new emojis are added or meanings are updated.",
)


@app.post(
    "/user/register",
    response_model=project.create_user_service.UserRegistrationResponse,
)
async def api_post_create_user(
    email: str, password: str, role: project.create_user_service.Role
) -> project.create_user_service.UserRegistrationResponse | Response:
    """
    Registers a new user profile.
    """
    try:
        res = await project.create_user_service.create_user(email, password, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/auth/login", response_model=project.login_user_service.LoginUserResponse)
async def api_post_login_user(
    email: str, password: str
) -> project.login_user_service.LoginUserResponse | Response:
    """
    Authenticates a user and returns an access token.
    """
    try:
        res = await project.login_user_service.login_user(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/emoji/interpret/{emoji}",
    response_model=project.interpret_emoji_service.InterpretEmojiResponse,
)
async def api_get_interpret_emoji(
    emoji: str,
) -> project.interpret_emoji_service.InterpretEmojiResponse | Response:
    """
    Returns the meaning of the input emoji.
    """
    try:
        res = await project.interpret_emoji_service.interpret_emoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put("/user/update", response_model=project.update_user_service.UpdateUserResponse)
async def api_put_update_user(
    id: str,
    email: str,
    password: str,
    role: project.update_user_service.Role,
    avatar_url: str,
) -> project.update_user_service.UpdateUserResponse | Response:
    """
    Updates an existing user profile.
    """
    try:
        res = await project.update_user_service.update_user(
            id, email, password, role, avatar_url
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/auth/logout", response_model=project.logout_user_service.LogoutResponse)
async def api_post_logout_user(
    auth_token: str,
) -> project.logout_user_service.LogoutResponse | Response:
    """
    Logs out a user, invalidating their access token.
    """
    try:
        res = await project.logout_user_service.logout_user(auth_token)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/user/activity",
    response_model=project.get_user_activity_service.UserActivityResponse,
)
async def api_get_get_user_activity() -> project.get_user_activity_service.UserActivityResponse | Response:
    """
    Retrieves the user's past emoji interpretation requests.
    """
    try:
        res = await project.get_user_activity_service.get_user_activity()
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
