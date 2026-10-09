from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_advertisement():
    response = client.post(
        "/advertisement",
        json={
            "title": "Книга по Python",
            "description": "Полезная литература для изучения FastAPI",
            "price": 1500,
            "author": "Иван",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Книга по Python"
    assert data["price"] == 1500
    assert "created_at" in data
    assert data["id"] == 1

    advertisement_id = data["id"]
    get_response = client.get(f"/advertisement/{advertisement_id}")

    assert get_response.status_code == 200
    assert get_response.json()["author"] == "Иван"


def test_update_and_delete_advertisement():
    create_response = client.post(
        "/advertisement",
        json={
            "title": "Ноутбук",
            "description": "Игровой ноутбук",
            "price": 50000,
            "author": "Мария",
        },
    )
    advertisement_id = create_response.json()["id"]

    update_response = client.patch(
        f"/advertisement/{advertisement_id}",
        json={"price": 45000, "title": "Ноутбук ASUS"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["price"] == 45000
    assert update_response.json()["title"] == "Ноутбук ASUS"

    delete_response = client.delete(f"/advertisement/{advertisement_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/advertisement/{advertisement_id}")
    assert get_response.status_code == 404


def test_search_advertisements_by_fields():
    client.post(
        "/advertisement",
        json={
            "title": "Мотоцикл",
            "description": "Рама и мотор",
            "price": 800000,
            "author": "Алексей",
        },
    )
    client.post(
        "/advertisement",
        json={
            "title": "Квартира",
            "description": "Двухкомнатная",
            "price": 5000000,
            "author": "Алексей",
        },
    )

    response = client.get("/advertisement?author=Алексей")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/advertisement?title=Мотоцикл")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Мотоцикл"

    response = client.get("/advertisement?price=5000000")
    assert response.status_code == 200
    assert response.json()[0]["price"] == 5000000
