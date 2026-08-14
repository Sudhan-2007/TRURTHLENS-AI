import pytest
from pymongo.errors import PyMongoError

from app import db as db_module
from app.db import (
    get_ai_explanations_collection,
    get_ai_predictions_collection,
    get_blacklist_collection,
    get_news_collection,
    get_official_sources_collection,
    get_trust_scores_collection,
    get_users_collection,
    get_verification_evidence_collection,
    get_verification_results_collection,
    ping_db,
)


async def test_ping_db_false_when_disconnected(monkeypatch):
    monkeypatch.setattr(db_module, "client", None)
    assert await ping_db() is False


async def test_ping_db_false_on_db_error(monkeypatch):
    class _FailingAdmin:
        async def command(self, *args, **kwargs):
            raise PyMongoError("database unreachable")

    class _FailingClient:
        admin = _FailingAdmin()

    monkeypatch.setattr(db_module, "client", _FailingClient())
    assert await ping_db() is False


@pytest.mark.parametrize(
    "getter",
    [
        get_users_collection,
        get_blacklist_collection,
        get_news_collection,
        get_ai_predictions_collection,
        get_official_sources_collection,
        get_verification_evidence_collection,
        get_verification_results_collection,
        get_trust_scores_collection,
        get_ai_explanations_collection,
    ],
)
def test_collection_getters_raise_when_disconnected(monkeypatch, getter):
    monkeypatch.setattr(db_module, "db", None)
    with pytest.raises(RuntimeError, match="Database not connected"):
        getter()
