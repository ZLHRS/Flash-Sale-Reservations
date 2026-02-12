import uuid
import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_cancel_reservation_returns_stock(client):
    r = await client.post(f"{API}/products", json={"name": "book", "stock": 1})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r.status_code == 201, r.text
    reservation_id = r.json()["id"]

    r = await client.post(f"{API}/reservations/{reservation_id}/cancel")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "canceled"
    assert body["canceled_at"] is not None

    r = await client.get(f"{API}/products/{product_id}")
    assert r.status_code == 200, r.text
    assert r.json()["stock"] == 1
