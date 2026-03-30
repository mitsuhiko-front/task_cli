print("🔥🔥🔥 このapi.pyが起動してる")
from fastapi import FastAPI
from service import CrudService
from exceptions import TaskNotFoundError, UserNotFoundError, HeaderNotFoundError, AutorizationError
from repository import TaskRepository, UserRepository
from query import TaskQueryService
from sqlite_db import SQLiteDatabase
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Depends
from typing import Literal
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi.security import HTTPBearer
from security import verify_password
from auth import create_access_token
from auth import get_current_user
from auth import create_access_token
from security import hash_password



security = HTTPBearer()

class TaskResponse(BaseModel):
    id: int
    description: str
    status: str
    createdAt: datetime
    updatedAt: datetime

class TaskWithUserResponse(BaseModel):
    id: int
    description: str
    status: str
    username: str

class TaskCreate(BaseModel):
    description: str

class TaskPut(BaseModel):
    description:str
    status: Literal["to-do", "in-progress", "done"]

class TaskPatch(BaseModel):
    description: Optional[str] = None
    status: Optional[Literal["to-do", "in-progress", "done"]] = None

app = FastAPI()

def get_service():
    db = SQLiteDatabase()
    db._create_tables()
    task_repo = TaskRepository(db)
    user_repo = UserRepository(db)
    query_repo = TaskQueryService(db)
    return CrudService(task_repo, user_repo, query_repo)

def get_user_repo():
    db = SQLiteDatabase()
    db._create_tables()
    return UserRepository(db)

#API例外ハンドラー
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Task not found"}
    )
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
        )
@app.exception_handler(ValueError)
async def invalid_value_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "invalid_value"}
    )
@app.exception_handler(HeaderNotFoundError)
async def invalid_value_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": "Header not found"}
    )
@app.exception_handler(AutorizationError)
async def Authorization_handler(request, exc):
    return JSONResponse(
        status_code=403, 
        content={"detail": "Authoraization Error"}
    )
#--------------------------------------
@app.post("/register")
def register(username: str, password: str, 
             user_repo: UserRepository = Depends(get_user_repo)):
    hashed = hash_password(password)

    user_repo.insert(username, hashed)

    return {"msg": "ok"}
#--------------------------------------
#ログインルーター
@app.post("/login")
def login(username: str, password: str, 
          user_repo: UserRepository = Depends(get_user_repo)):
    user = user_repo.find_by_username(username)
    if user is None:
        raise HTTPException(status_code=401)
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401)
    token = create_access_token(user["id"])
    return {"access_token": token}
#--------------------------------------

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(service: CrudService = Depends(get_service),
               user=Depends(get_current_user)):
    tasks = service.list_tasks(user["id"])
    for t in tasks:
        print(t.to_dict())
    return [TaskResponse(
        id=t.id,
        description=t.description,
        status=t.status,
        createdAt=t.createdAt,
        updatedAt=t.updatedAt
    ) for t in tasks]   
 
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, 
                   user=Depends(get_current_user),
                   service: CrudService = Depends(get_service)):
    task = service.get_task_by_id(task_id, user["id"])
    return TaskResponse(**task.to_dict()) 

@app.get("/tasks-with-user", response_model=list[TaskWithUserResponse])
def list_tasks_with_user(service: CrudService = Depends(get_service),
                         user = Depends(get_current_user)):
    tasks = service.list_tasks_with_user(user["id"])
    return [TaskWithUserResponse(**t) for t in tasks]

@app.get("/tasks-with-user/{task_id}", response_model=TaskWithUserResponse)
def get_task_with_user_by_id(task_id: int, 
                             user=Depends(get_current_user),
                             service: CrudService = Depends(get_service)):
    task = service.get_task_with_user_by_id(task_id, user["id"])
    return TaskWithUserResponse(**task) 
#--------------------------------------
@app.post("/tasks")
def create_task(task: TaskCreate, 
                user=Depends(get_current_user), 
                service: CrudService = Depends(get_service)):
    created = service.add(task.description, user["id"])
    return created
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, 
                user = Depends(get_current_user),
                service: CrudService = Depends(get_service)):
    service.delete(task_id, user["id"])


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def put_task(task_id: int, 
             task: TaskPut, 
             user = Depends(get_current_user),
             service: CrudService = Depends(get_service)):
    updated = service.update(task_id, task.description, task.status, user["id"])
    return TaskResponse(**updated.to_dict())

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, task: TaskPatch, 
               user = Depends(get_current_user), 
               service: CrudService = Depends(get_service)):
        patched = service.patch(task_id, user["id"], task.description, task.status)
        return TaskResponse(
            id=patched.id,
            description=patched.description,
            status=patched.status,
            createdAt=patched.createdAt,
            updatedAt=patched.updatedAt
        )


