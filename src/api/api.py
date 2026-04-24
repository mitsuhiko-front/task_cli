print("🔥🔥🔥 このapi.pyが起動してる")
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from src.service.service import CrudService
from src.exceptions import TaskNotFoundError, UserNotFoundError, HeaderNotFoundError, AlreadyDeletedError, NotDeletedError, AuthorizationError
from src.repository.user_repository import UserRepository
from src.repository.task_repository import TaskRepository
from src.repository.query_repository import TaskQueryService
from src.database.postgre_db import get_db
from src.database.postgre_db import create_db
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Depends
from typing import Literal
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi.security import HTTPBearer
from src.security.security import verify_password
from src.security.security import hash_password
from src.auth.auth import create_access_token
from src.auth.auth import get_current_user





security = HTTPBearer()

class TaskResponse(BaseModel):
    id: int
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task):
        return cls(
            id=task.id,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
class TaskWithUserResponse(BaseModel):
    id: int
    description: str
    status: str
    username: str

    @classmethod
    def from_query(cls, task):
        return cls(**task)
    
class TaskCreate(BaseModel):
    description: str

class TaskPut(BaseModel):
    description:str
    status: Literal["to-do", "in-progress", "done"]

class TaskPatch(BaseModel):
    description: Optional[str] = None
    status: Optional[Literal["to-do", "in-progress", "done"]] = None

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = create_db()
    try:
        db.create_tables()
        logger.info("database tables created")
        yield
    finally:
        db.close()
        logger.info("database connection closed")
app = FastAPI(lifespan=lifespan)

def get_service(db=Depends(get_db)):
    
    return CrudService(TaskRepository(db), UserRepository(db), TaskQueryService(db))

def get_user_repo(db=Depends(get_db)):
    
    return UserRepository(db)

#API例外ハンドラー
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Task not found"}
    )
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)}
        )
@app.exception_handler(HeaderNotFoundError)
async def header_not_found_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"message": "Header not found"}
    )
@app.exception_handler(AlreadyDeletedError)
def handle_deleted(request, exc):
    return JSONResponse(
        status_code=409,
        content={"message": "Task already deleted"}
    )
@app.exception_handler(NotDeletedError)
def handle_not_deleted(request, exc):
    return JSONResponse(
        status_code=409,
        content={"message": "Task is not deleted"}
    )
@app.exception_handler(AuthorizationError)
async def Authorization_handler(request, exc):
    return JSONResponse(
        status_code=403, 
        content={"message": "Not allowed"}
    )
    #--------------------------------------
@app.post("/register")
def register(body: RegisterRequest, 
            user_repo: UserRepository = Depends(get_user_repo)):
    hashed = hash_password(body.password)

    user_repo.insert(body.username, hashed)
    return {"msg": "ok"}
#--------------------------------------
#ログインルーター
@app.post("/login")
def login(body: LoginRequest, 
          user_repo: UserRepository = Depends(get_user_repo)):
    user = user_repo.find_by_username(body.username)
    if user is None:
        raise HTTPException(status_code=401)
    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401)
    token = create_access_token(user["id"])
    return {"access_token": token}
#--------------------------------------

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(service: CrudService = Depends(get_service),
               user=Depends(get_current_user)):
    tasks = service.list_tasks(user["id"])
    
    return [TaskResponse.from_domain(t) for t in tasks]   
 
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, 
                   user=Depends(get_current_user),
                   service: CrudService = Depends(get_service)):
    task = service.get_task_by_id(task_id, user["id"])
    return TaskResponse.from_domain(task) 

@app.get("/tasks-with-user", response_model=list[TaskWithUserResponse])
def list_tasks_with_user(service: CrudService = Depends(get_service),
                         user = Depends(get_current_user)):
    tasks = service.list_tasks_with_user(user["id"])
    return [TaskWithUserResponse.from_query(t) for t in tasks]

@app.get("/tasks-with-user/{task_id}", response_model=TaskWithUserResponse)
def get_task_with_user_by_id(task_id: int, 
                             user=Depends(get_current_user),
                             service: CrudService = Depends(get_service)):
    task = service.get_task_with_user_by_id(task_id, user["id"])
    return TaskWithUserResponse.from_query(task) 

@app.get("/tasks/status/{status}", response_model=list[TaskResponse])
def list_tasks_by_status(status: str,
                         user=Depends(get_current_user),
                         service: CrudService = Depends(get_service)):
   
    tasks = service.list_tasks_by_status(status, user["id"])
    return [TaskResponse.from_domain(t) for t in tasks]

#--------------------------------------
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, 
                user=Depends(get_current_user), 
                service: CrudService = Depends(get_service)):
    created = service.add(task.description, user["id"])
    return TaskResponse.from_domain(created)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, 
                user = Depends(get_current_user),
                service: CrudService = Depends(get_service)):
    service.delete(task_id, user["id"])
    return 

@app.post("/tasks/{task_id}/restore", status_code=200)
def restore_task(task_id: int, 
                 user = Depends(get_current_user),
                 service: CrudService = Depends(get_service)):
    restored = service.restore(task_id, user["id"])
    return TaskResponse.from_domain(restored)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def put_task(task_id: int, 
             task: TaskPut, 
             user = Depends(get_current_user),
             service: CrudService = Depends(get_service)):
    updated = service.update(task_id, task.description, task.status, user["id"])
    return TaskResponse.from_domain(updated)

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, task: TaskPatch, 
               user = Depends(get_current_user), 
               service: CrudService = Depends(get_service)):
        patched = service.patch(task_id, user["id"], task.description, task.status)
        return TaskResponse.from_domain(patched)


