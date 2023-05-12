"""
@created_by ayaan
@created_at 2023.05.12
"""
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_blobs_list():
    response = client.get("/blobs")
    print(response)
    assert response.status_code == 200
    # assert type(response)
