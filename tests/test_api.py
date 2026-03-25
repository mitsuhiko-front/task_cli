from fastapi.testclient import TestClient
from api import app
from auth import get_user_repo


class FakeUserRepo:
    def find_by_id(self, user_id: int):
        if user_id == 1:
            return {"id": 1, "username": "test-user"}
        return None


def override_get_user_repo():
    return FakeUserRepo()


#公式テスト用
app.dependency_overrides[get_user_repo] = override_get_user_repo

client = TestClient(app)


def test_create_task():
    response = client.post(
        "/tasks",
        headers={"Authorization": "Bearer 1"},
        json={"description": "test task"},
    )

    assert response.status_code == 200