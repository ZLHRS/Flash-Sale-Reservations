import uuid
import pytest
from sqlalchemy import select

from infrastructure.models.outbox_event_model import OutboxEventModel

API = "/api/v1"


@pytest.mark.asyncio
async def test_main_flow_create_product_reserve_confirm_and_outbox(
    client, sessionmaker
):
    r = await client.post(f"{API}/products", json={"name": "ps5", "stock": 1})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations",
        json={"product_id": product_id, "user_id": user_id},
    )
    assert r.status_code == 201, r.text
    reservation_id = r.json()["id"]
    assert r.json()["status"] == "active"

    r = await client.post(f"{API}/reservations/{reservation_id}/confirm")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "confirmed"
    assert body["confirmed_at"] is not None

    r = await client.get(f"{API}/products/{product_id}")
    assert r.status_code == 200, r.text
    assert r.json()["stock"] == 0

    async with sessionmaker() as s:
        res = await s.execute(
            select(OutboxEventModel).order_by(OutboxEventModel.created_at.desc())
        )
        event = res.scalars().first()
        assert event is not None, "Outbox event was not created"
        assert event.event_type == "reservation_confirmed"
        assert event.payload["reservation_id"] == str(reservation_id)
        assert event.payload["user_id"] == str(user_id)
        assert event.payload["product_id"] == str(product_id)
