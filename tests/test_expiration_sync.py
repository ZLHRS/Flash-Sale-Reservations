import uuid
import pytest
from datetime import datetime, UTC, timedelta

from sqlalchemy import text

API = "/api/v1"


@pytest.mark.asyncio
async def test_expiration_via_sync_expired_marks_expired_and_returns_stock(
    client, sessionmaker
):
    r = await client.post(f"{API}/products", json={"name": "gpu", "stock": 1})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r.status_code == 201, r.text
    reservation_id = r.json()["id"]

    past = datetime.now(UTC) - timedelta(seconds=10)
    async with sessionmaker() as s:
        await s.execute(
            text("UPDATE reservations SET expires_at=:past WHERE id=:rid"),
            {"past": past, "rid": reservation_id},
        )
        await s.commit()

    r = await client.post(f"{API}/admin/sync-expired")
    assert r.status_code == 200, r.text
    assert r.json()["expired_processed"] >= 1

    r = await client.get(f"{API}/reservations/{reservation_id}")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "expired"

    r = await client.get(f"{API}/products/{product_id}")
    assert r.status_code == 200, r.text
    assert r.json()["stock"] == 1
