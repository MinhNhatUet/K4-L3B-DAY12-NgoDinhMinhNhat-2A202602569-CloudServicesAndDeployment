"""Boundary and integration checks for the CP3 protection layers."""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.cost_guard import CostGuard, KEY_TTL_SECONDS
from app.rate_limiter import RateLimiter, WINDOW_SECONDS


def test_same_timestamp_and_window_boundary(fake_redis):
    limiter = RateLimiter(fake_redis, 2)
    limiter.check("u", now=1000)
    limiter.check("u", now=1000)
    assert limiter.hit_count("u", now=1000) == 2
    assert 0 < fake_redis.ttl(limiter._key("u")) <= WINDOW_SECONDS
    with pytest.raises(HTTPException) as error:
        limiter.check("u", now=1000)
    assert error.value.headers["Retry-After"] == "60"
    assert limiter.hit_count("u", now=1000) == 2
    limiter.check("u", now=1060)
    assert limiter.hit_count("u", now=1060) == 1


def test_month_isolation_budget_boundary_and_ttl(fake_redis):
    guard = CostGuard(fake_redis, 1.0)
    assert guard.record("u", 0.75, month="2026-09") == pytest.approx(0.75)
    guard.check("u", estimated_cost=0.25, month="2026-09")
    with pytest.raises(HTTPException) as error:
        guard.check("u", estimated_cost=0.26, month="2026-09")
    assert error.value.status_code == 402
    assert guard.spent("u", month="2026-10") == 0.0
    assert 0 < fake_redis.ttl(guard._key("u", "2026-09")) <= KEY_TTL_SECONDS


@pytest.mark.parametrize("blocked_status", [401, 429, 402])
def test_blocked_requests_never_call_llm(
    blocked_status, client_factory, fake_redis, auth_headers, monkeypatch
):
    llm = Mock(side_effect=AssertionError("Blocked request reached LLM"))
    monkeypatch.setattr("app.main.ask_llm", llm)
    client = client_factory(rate_limit=0 if blocked_status == 429 else 10)
    if blocked_status == 402:
        fake_redis.set(CostGuard._key("sv-test"), "999")
    response = client.post(
        "/ask", json={"question": "Hello"},
        headers={} if blocked_status == 401 else auth_headers,
    )
    assert response.status_code == blocked_status
    llm.assert_not_called()
    if blocked_status == 401:
        assert not fake_redis.keys("ratelimit:*")


def test_ask_persists_history_and_cost(client_real_store, fake_redis, auth_headers):
    from app.store import ConversationStore

    first = client_real_store.post(
        "/ask", json={"question": "Docker là gì?"}, headers=auth_headers
    )
    assert first.status_code == 200
    assert first.json()["history_length"] == 0
    second = client_real_store.post(
        "/ask", json={"question": "Giải thích thêm"}, headers=auth_headers
    )
    assert second.status_code == 200
    assert second.json()["history_length"] == 2
    history = ConversationStore(fake_redis).get_history("sv-test")
    assert [item["role"] for item in history] == ["user", "assistant"] * 2
    assert CostGuard(fake_redis, 10).spent("sv-test") == pytest.approx(
        first.json()["cost_usd"] + second.json()["cost_usd"]
    )
