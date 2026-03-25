print("🔥🔥🔥 このapi.pyが起動してる")
from fastapi import FastAPI
from service import CrudService
from exceptions import TaskNotFoundError, UserNotFoundError, HeaderNotFoundError
from repository import TaskRepository, UserRepository
from query import TaskQueryService
from sqlite_db import SQLiteDatabase
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Depends
from typing import Literal
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

security = HTTPBearer()

class TaskResponse(BaseModel):
    id: int
    description: str
    status: str
    createdAt: str
    updatedAt: str

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
def authenticate_user(authorization: str):
    parts = authorization.split()

    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id = int(parts[1])
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = user_repo.find_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_id = int(credentials.credentials)
    user = user_repo.find_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401)

    return user
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
#--------------------------------------
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    tasks = service.list_tasks()
    return [ TaskResponse(**t) for t in tasks]   
 
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int):
    task = service.get_task_by_id(task_id)
    return TaskResponse(**task) 

@app.get("/tasks-with-user", response_model=list[TaskWithUserResponse])
def list_tasks_with_user():
    tasks = service.list_tasks_with_user()
    return [TaskWithUserResponse(**t) for t in tasks]

@app.get("/tasks-with-user/{task_id}", response_model=TaskWithUserResponse)
def get_task_with_user_by_id(task_id: int):
    task = service.get_task_with_user_by_id(task_id)
    return TaskWithUserResponse(**task) 
#--------------------------------------
@app.post("/tasks")
def create_task(task: TaskCreate, user=Depends(get_current_user)):
    return service.add(task.description, user["id"])

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
        service.delete(task_id)
    
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def put_task(task_id: int, task: TaskPut):
    #task_id == 
    #task == TaskPut(description="", status="")
    updated = service.update(task_id, task.description, task.status)
    return TaskResponse(**updated.to_dict())

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, task: TaskPatch):
        patched = service.patch(task_id, task.description, task.status)
        return TaskResponse(**patched.to_dict())

db = SQLiteDatabase()
db._create_tables()
task_repo = TaskRepository(db)
user_repo = UserRepository(db)
query_repo = TaskQueryService(db)
service = CrudService(task_repo, user_repo, query_repo)