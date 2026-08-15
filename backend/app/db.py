from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import InvalidOperation, PyMongoError

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
    except (InvalidOperation, PyMongoError):
        return False


def get_users_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["users"]


def get_blacklist_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["token_blacklist"]


def get_news_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["news_submissions"]


def get_ai_predictions_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["ai_predictions"]


def get_official_sources_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["official_sources"]


def get_verification_evidence_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["verification_evidence"]


def get_verification_results_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["verification_results"]


def get_trust_scores_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["trust_scores"]


def get_ai_explanations_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["ai_explanations"]


def get_feedback_collection():
    if db is None:
        raise RuntimeError("Database not connected")
    return db["feedback"]


async def init_indexes() -> None:
    users = get_users_collection()
    await users.create_index("email", unique=True)
    blacklist = get_blacklist_collection()
    await blacklist.create_index("exp", expireAfterSeconds=0)
    news = get_news_collection()
    await news.create_index("submission_id", unique=True)
    await news.create_index("user_id")
    predictions = get_ai_predictions_collection()
    await predictions.create_index("submission_id", unique=True)
    await predictions.create_index("user_id")
    sources = get_official_sources_collection()
    await sources.create_index("domain", unique=True)
    evidence = get_verification_evidence_collection()
    await evidence.create_index("submission_id")
    results = get_verification_results_collection()
    await results.create_index("submission_id", unique=True)
    trust_scores = get_trust_scores_collection()
    await trust_scores.create_index("submission_id", unique=True)
    explanations = get_ai_explanations_collection()
    await explanations.create_index("submission_id", unique=True)
    feedback = get_feedback_collection()
    await feedback.create_index("submission_id")


def close_db() -> None:
    global client, db
    if client is not None:
        client.close()
    client = None
    db = None
