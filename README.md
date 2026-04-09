#  Task Management API

FastAPIを用いたタスク管理APIです。  
ユーザー認証（JWT）を行い、ユーザーごとにタスクを管理できます。

---

##  デモ

Renderでデプロイ済み  


##  技術スタック

- Python
- FastAPI
- PostgreSQL
- psycopg2
- JWT認証
- pwdlib (パスワードハッシュ化)
  

---

##  機能一覧

### 認証
- ユーザー登録
- ログイン（JWT発行）

### タスク管理
- タスク作成
- タスク一覧取得
- タスク更新
- タスク削除（論理削除）

### その他
- ユーザーとタスクのJOIN取得

---

##  認証について

ログイン後にJWTトークンを発行 
リクエスト時に以下のヘッダーを付与します。

トークンからuser_idを取得 
ユーザーごとにデータを分離しています。

---

##  DB設計

### users

| カラム | 型 | 説明 |
|------|----|------|
| id | SERIAL | 主キー |
| username | TEXT | ユーザー名（ユニーク） |
| password | TEXT | ハッシュ化パスワード |

---

### tasks

| カラム | 型 | 説明 |
|------|----|------|
| id | SERIAL | 主キー |
| description | TEXT | タスク内容 |
| status | TEXT | 状態 |
| user_id | INTEGER | ユーザーID |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |
| deleted_at | TIMESTAMP | 論理削除 |

---

##  API一覧

| メソッド | エンドポイント | 説明 |
|--------|--------------|------|
| POST | /register | ユーザー登録 |
| POST | /login | ログイン |
| GET | /tasks | タスク一覧 |
| POST | /tasks | タスク作成 |
| PATCH | /tasks/{id} | 更新 |
| DELETE | /tasks/{id} | 削除 |

---

##  セットアップ方法

```bash
git clone <repo>
cd project

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn src.api.api:app --reload
