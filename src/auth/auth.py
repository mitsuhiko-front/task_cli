from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from jose import JWTError
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from src.repository.user_repository import UserRepository
from src.database.postgre_db import get_db
from src.database.postgre_db import create_db
from fastapi import Depends

#自動でBearer付ける
security = HTTPBearer()

SECRET_KEY = "secret"
ALGORITHM = "HS256"

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])

def get_user_repo():
    db = create_db()
    return UserRepository(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    user_repo: UserRepository = Depends(get_user_repo)
):
    
    try:
        user_id = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401)
    user = user_repo.find_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


    
