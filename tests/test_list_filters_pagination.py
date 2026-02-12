import uuid
import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_list_reservations_filter_by_user_and_status_with_pagination(client):
    r = await client.post(f"{API}/products", json={"name": "bulk", "stock": 5})
    assert r.status_code == 201, r.text
    product_id = r.json()["id"]

    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())

    r1 = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user1}
    )
    assert r1.status_code == 201, r1.text
    r2 = await client.post(
        f"{API}/reservations", json={"product_id": product_id, "user_id": user2}
    )
    assert r2.status_code == 201, r2.text

    rid2 = r2.json()["id"]
    r = await client.post(f"{API}/reservations/{rid2}/confirm")
    assert r.status_code == 200, r.text

    r = await client.get(
        f"{API}/reservations",
        params={
            "user_id": user2,
            "reservation_status": "confirmed",
            "page": 1,
            "size": 10,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pagination"]["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["user_id"] == user2
    assert body["items"][0]["status"] == "confirmed"

    r = await client.get(f"{API}/reservations", params={"page": 1, "size": 1})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pagination"]["size"] == 1
    assert body["pagination"]["total_pages"] >= 1
