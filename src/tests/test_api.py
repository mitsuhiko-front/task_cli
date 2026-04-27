from fastapi.testclient import TestClient
from src.api.api import app

client = TestClient(app)

def test_task_flow():
    # ① ユーザー登録
    register_res = client.post("/register", json={
        "username": "testuser2",
        "password": "testpass"
    })
    assert register_res.status_code == 200

    # ② ログイン
    login_res = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ③ タスク作成
    create_res = client.post("/tasks", json={
        "description": "テストタスク"
    }, headers=headers)
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]

    # ④ タスク一覧取得
    list_res = client.get("/tasks", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) > 0

    # ⑤ タスク1件取得
    get_res = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id

    # ⑥ タスク更新（PUT）
    put_res = client.put(f"/tasks/{task_id}", json={
        "description": "更新後タスク",
        "status": "in-progress"
    }, headers=headers)
    assert put_res.status_code == 200
    assert put_res.json()["status"] == "in-progress"

    # ⑦ タスク部分更新（PATCH）
    patch_res = client.patch(f"/tasks/{task_id}", json={
        "status": "done"
    }, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "done"

    # ⑧ タスク削除
    delete_res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_res.status_code == 204

    # ⑨ タスク復元
    restore_res = client.post(f"/tasks/{task_id}/restore", headers=headers)
    assert restore_res.status_code == 200

def test_unauthorized():
    # 未ログインでアクセス → 401
    res = client.get("/tasks")
    assert res.status_code == 401

def test_task_not_found():
    # ログイン
    login_res = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 存在しないタスク → 404
    res = client.get("/tasks/99999", headers=headers)
    assert res.status_code == 404