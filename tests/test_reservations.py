import uuid
import asyncio
import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_no_double_active_reservation_same_user_product(client):
    r = await client.post(f"{API}/products", json={"name": "book", "stock": 2})
    assert r.status_code in (200, 201), r.text
    product_id = r.json()["id"]

    user_id = str(uuid.uuid4())

    r1 = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r1.status_code == 201, r1.text

    r2 = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user_id}
    )
    assert r2.status_code == 409, r2.text


@pytest.mark.asyncio
async def test_concurrent_reserve_last_stock(client):
    r = await client.post(f"{API}/products", json={"name": "gpu", "stock": 1})
    assert r.status_code in (200, 201), r.text
    product_id = r.json()["id"]

    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())

    async def reserve(uid):
        return await client.post(
            f"{API}/reservations", json={"product_id": product_id, "user_id": uid}
        )

    r1, r2 = await asyncio.gather(reserve(user1), reserve(user2))
    assert sorted([r1.status_code, r2.status_code]) == [201, 409], (r1.text, r2.text)

    r = await client.get(f"{API}/products/{product_id}")
    assert r.status_code == 200, r.text
    assert r.json()["stock"] == 0
