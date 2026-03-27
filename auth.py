from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from repository import UserRepository
from sqlite_db import SQLiteDatabase
from fastapi import Depends
security = HTTPBearer()

SECRET_KEY = "secret"
ALGORITHM = "HS256"

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])

def get_user_repo():
    db = SQLiteDatabase()
    db._create_tables()
    return UserRepository(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    user_repo: UserRepository = Depends(get_user_repo)
):
    try:
        user_id = decode_token(credentials.credentials)
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = user_repo.find_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


    
