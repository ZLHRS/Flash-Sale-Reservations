import uuid
import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_cannot_confirm_canceled_reservation(client):
    r = await client.post(f"{API}/products", json={"name": "item", "stock": 1})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    r = await client.post(f"{API}/reservations/{rid}/cancel")
    assert r.status_code == 200, r.text

    r = await client.post(f"{API}/reservations/{rid}/confirm")
    assert r.status_code == 409, r.text


@pytest.mark.asyncio
async def test_cannot_cancel_confirmed_reservation(client):
    r = await client.post(f"{API}/products", json={"name": "item2", "stock": 1})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())
    r = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    r = await client.post(f"{API}/reservations/{rid}/confirm")
    assert r.status_code == 200, r.text

    r = await client.post(f"{API}/reservations/{rid}/cancel")
    assert r.status_code == 409, r.text
