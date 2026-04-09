
from src.model.model import TaskProperty
from src.exceptions import TaskNotFoundError, UserNotFoundError, AuthorizationError, AlreadyDeletedError, NotDeletedError, AuthenticationError
from src.security.security import verify_password, hash_password
from src.auth.auth import create_access_token


class CrudService():
    def __init__(self, task_repo, user_repo, query_repo):
        self.task_repo = task_repo
        self.user_repo = user_repo
        self.query_repo = query_repo

    def add(self, description: str, user_id):
        task = TaskProperty(
            id=None,
            description=description,
            status="to-do",
            user_id=user_id,
            created_at=None,
            updated_at=None,
            deleted_at=None
        )
    
        new_id = self.task_repo.insert(task)

        return self.task_repo.find_by_id(new_id)
        
    def delete(self, task_id: int, user_id: int):
        task = self.get_task_or_404(task_id)

        if task.user_id != user_id:
            raise AuthorizationError()

        if task.deleted_at is not None:
            raise AlreadyDeletedError("削除済みです")
        return self.task_repo.delete(task_id)

    def restore(self, task_id: int, user_id: int):
        task = self.task_repo.find_by_deleted_id(task_id)
        if task is None:
            raise TaskNotFoundError()
        
        if task.user_id != user_id:
            raise AuthorizationError()
        
        if task.deleted_at is None:
            raise NotDeletedError("未削除です")
        
        restored = self.task_repo.restore(task_id)
        if not restored:
            raise TaskNotFoundError()
        return True
        
    def update(self, task_id: int, new_description: str, new_status: str, user_id: int):
        task = self.get_task_or_404(task_id)

        if task.user_id != user_id:
            raise AuthorizationError()
        task.replace(new_description, new_status)
        
        updated = self.task_repo.update(task)

        if not updated:
            raise TaskNotFoundError("タスクがありません")
        return task
       
    def patch(self, task_id: int, user_id: int, description: str | None = None, status: str | None = None):
        task = self.get_task_or_404(task_id)

        if task.user_id != user_id:
            raise AuthorizationError()
        changed = task.patch(description, status)

        if not changed:     
            return task
        updated = self.task_repo.update(task)

        if not updated:
            raise TaskNotFoundError()
        
        return self.task_repo.find_by_id(task.id)
    
         
    def list_tasks(self, user_id: int):
        
        return self.task_repo.find_all(user_id)
    
    def list_tasks_with_user(self, user_id: int):
        return self.query_repo.find_all_with_user(user_id)
    
    def get_task_by_id(self, task_id: int, user_id: int):
        task = self.get_task_or_404(task_id)
        if task.user_id != user_id:
            raise AuthorizationError()
        return task
    def get_task_with_user_by_id(self, task_id: int, user_id: int):
        task_find = self.get_task_or_404(task_id)
        if task_find.user_id != user_id:
            raise AuthorizationError()
        task = self.query_repo.find_task_with_user_by_id(task_id)
        
        if task is None:
            raise TaskNotFoundError()

        return task
    
    def list_tasks_by_status(self, status: str, user_id: int):
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise AuthorizationError()
        if user["id"] != user_id:
            raise AuthorizationError()
        if status not in ("done", "in-progress", "to-do"):
            raise ValueError("ステータスが不正です")
        
        return self.task_repo.find_by_status(status)
    
    def find_user_by_id(self, user_id: int):
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
    def get_task_or_404(self, task_id):
        task = self.task_repo.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("")
        return task
#----------------------------------------------------   
    def register(self, username, password):
        hashed = hash_password(password)

        self.user_repo.insert(username, hashed)

    def login(self, username, password):
        user = self.user_repo.find_by_username(username)

        if not user:
            raise AuthenticationError
        
        if not verify_password(password, user["password"]):
            raise AuthenticationError
        return create_access_token(user["id"])
    
    def list_sts(self, status):
        tasks = self.repo.load_tasks()
        if not tasks:
            raise TaskNotFoundError("タスクがありません")
        if status not in ("done", "in-progress", "to-do"):
            raise ValueError("ステータスが不正です")    
        new_tasks = [t for t in tasks if t.status == status]
        return new_tasks

    def mark(self, status, task_id: int):
    
        valid_status = {
        "done": "done",
        "to-do": "to-do",
        "in-progress": "in-progress"
    }
        
        if status not in valid_status:
            raise ValueError("ステータスが不正です")
        tasks = self.repo.load_tasks()
        task = self._find_task(tasks, task_id)
        task.change_status(valid_status[status])     
        self.repo.save_tasks(tasks)
        return 
    
    def _find_task(self, tasks, task_id):
        for task in tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError("タスクがありません")

   



