from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from repository import UserRepository
from sqlite_db import SQLiteDatabase
from fastapi import Depends
security = HTTPBearer()

def get_user_repo():
    db = SQLiteDatabase()
    db._create_tables()
    return UserRepository(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    user_repo: UserRepository = Depends(get_user_repo)
):
    user_id = int(credentials.credentials)
    user = user_repo.find_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


    
