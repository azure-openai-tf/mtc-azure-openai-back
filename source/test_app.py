"""
@created_by ayaan
@created_at 2023.05.12
"""
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_container_list():
    response = client.get("/containers")
    print(response.json())
    assert response.status_code == 200
    # assert type(response)
