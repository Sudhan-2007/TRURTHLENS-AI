from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

from .config import settings

client: AsyncIOMotorClient | None = None
db = None


def connect_db() -> None:
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DB]


async def ping_db() -> bool:
    if client is None:
        return False
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False


def close_db() -> None:
    global client, db
    if client is not None:
        client.close()
    client = None
    db = None
