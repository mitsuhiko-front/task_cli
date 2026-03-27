
from model import TaskProperty
from exceptions import TaskNotFoundError
from exceptions import UserNotFoundError

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
            createdAt=None,
            updatedAt=None,
            deletedAt=None
        )
    
        return self.task_repo.insert(task)
      
        
    def delete(self, task_id: int):
        task = self.get_task_or_404(task_id)

        if task.deletedAt is not None:
            raise ValueError("削除済みです")
        self.task_repo.delete(task_id)

    def restore(self, task_id):
        task = self.get_task_or_404(task_id)

        if task.deletedAt is None:
            raise ValueError("未削除です")
        self.task_repo.restore(task_id)

    def update(self, task_id: int, new_description: str, new_status: str):
        task = self.get_task_or_404(task_id)
        task.replace(new_description, new_status)
        
        updated = self.task_repo.update(task)

        if not updated:
            raise TaskNotFoundError("タスクがありません")
        return task
       
    def patch(self, task_id: int, description: str | None = None, status: str | None = None):
        task = self.get_task_or_404(task_id)
        changed = task._patch(description, status)

        if changed:     
            self.task_repo.update(task)
        return task
            
    def list_tasks(self):
        return self.task_repo.find_all()
    
    def list_tasks_with_user(self):
        return self.query_repo.find_all_with_user()
    
    def get_task_by_id(self, task_id: int):
        task = self.get_task_or_404(task_id)
        return task
    def get_task_with_user_by_id(self, task_id: int):
        task = self.query_repo.find_task_with_user_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        return task
    
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

   


class TaskNotFoundError(Exception):
    pass

