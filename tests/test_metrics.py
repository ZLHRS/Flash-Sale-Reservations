import uuid
import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_metrics_created_confirmed_canceled_expired_increment(
    client, sessionmaker
):
    r = await client.get(f"{API}/admin/metrics")
    assert r.status_code == 200, r.text
    m0 = r.json()

    r = await client.post(f"{API}/products", json={"name": "m", "stock": 3})
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    u1 = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": pid, "user_id": u1}
    )
    assert r.status_code == 201, r.text
    rid1 = r.json()["id"]
    r = await client.post(f"{API}/reservations/{rid1}/confirm")
    assert r.status_code == 200, r.text

    u2 = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": pid, "user_id": u2}
    )
    assert r.status_code == 201, r.text
    rid2 = r.json()["id"]
    r = await client.post(f"{API}/reservations/{rid2}/cancel")
    assert r.status_code == 200, r.text

    u3 = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": pid, "user_id": u3}
    )
    assert r.status_code == 201, r.text
    rid3 = r.json()["id"]

    from datetime import datetime, UTC, timedelta
    from sqlalchemy import text

    past = datetime.now(UTC) - timedelta(seconds=10)
    async with sessionmaker() as s:
        await s.execute(
            text("UPDATE reservations SET expires_at=:p WHERE id=:rid"),
            {"p": past, "rid": rid3},
        )
        await s.commit()
    r = await client.post(f"{API}/admin/sync-expired")
    assert r.status_code == 200, r.text

    r = await client.get(f"{API}/admin/metrics")
    assert r.status_code == 200, r.text
    m1 = r.json()

    def get(d, key):
        v = d.get(key)
        return int(v) if v is not None else 0

    assert get(m1, "reservations_created") >= get(m0, "reservations_created") + 3
    assert get(m1, "reservations_confirmed") >= get(m0, "reservations_confirmed") + 1
    assert get(m1, "reservations_canceled") >= get(m0, "reservations_canceled") + 1
    assert get(m1, "reservations_expired") >= get(m0, "reservations_expired") + 1
