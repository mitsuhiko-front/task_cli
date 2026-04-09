import sys
from src.service.service import CrudService
from src.repository.task_repository import TaskRepository
from src.repository.user_repository import UserRepository
from src.repository.query_repository import TaskQueryService
from src.database.sqlite_db import SQLiteDatabase
from exceptions import TaskNotFoundError
from auth.auth import decode_token

def get_service():
    db = SQLiteDatabase()
    db._create_tables()
    task_repo = TaskRepository(db)
    user_repo = UserRepository(db)
    query_repo = TaskQueryService(db)
    return CrudService(task_repo, user_repo, query_repo)

def get_user_id():
    token = input("token: ")
    return decode_token(token)

def print_task(task):
    print(f"[{task.id}] {task.description} ({task.status})")

def print_task_with_user(task):
    print(f"[{task["id"]}] {task["description"]} ({task["status"]}) <{task["username"]}>")

def main():
    if len(sys.argv) < 2:
        print("usage: <command> [args]")
        return
    service = get_service()
    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "register":cmd_register,
        "login":cmd_login,
        "add": cmd_add,
        "delete": cmd_delete,
        "update": cmd_update,
        "list": cmd_list,
        "list_by_id":cmd_list_by_id,
        "list_with_user": cmd_list_with_user,
        "list_with_user_by_id":cmd_list_with_user_by_id
    }

    if command not in commands:
        print("error command")
        return

    commands[command](service, args)

def cmd_register(service, args):
    username = input("username: ")
    password = input("password: ")

    try:
        service.register(username, password)
        print("ユーザー登録しました")
    except Exception:
        print("登録に失敗しました")

def cmd_login(service, args):
    username = input("username: ")
    password = input("password: ")

    token = service.login(username, password)
    print(f"token: {token}")

def cmd_add(service, args):    
    if len(args) < 1:
        print("usage: add <description>")
        return

    description = args[0]
    service.add(description)
    print("追加しました")  
def cmd_delete(service, args): 
    if len(args) < 1:
        print("usage: delete <id>")
        return
    try:
        task_id = int(args[0])
        service.delete(task_id)
        print("削除しました")
    except ValueError:
        print("IDが不正です")
    except TaskNotFoundError:
        print("見つかりません")
def cmd_update(service, args):
    if len(args) < 1:
        print("usage: update <id> <description> <status>")
        return    
    
    task_id = int(args[0])
    description = args[1]
    status = args[2]
    try:
        service.update(task_id, description, status)
        print("更新しました")
    except ValueError:
        print("IDが不正です")    
    except TaskNotFoundError:
        print("見つかりません")
    
def cmd_list(service, args):
    user_id = get_user_id()
    tasks = service.list_tasks(user_id)
    for t in tasks:
        print_task(t)

def cmd_list_by_id(service, args):
    if len(args) < 1:
        print("usage: list_by_id <id>")
    task_id = int(args[0])
    user_id = get_user_id()
    task = service.get_task_by_id(task_id, user_id)
    print_task(task)

def cmd_list_with_user(service, args):
    user_id = get_user_id()
    tasks = service.list_tasks_with_user(user_id)
    for t in tasks:
        print_task_with_user(t)

def cmd_list_with_user_by_id(service, args):
    if len(args) < 1:
        print("usage: list_with_user_by_id <id>")
    task_id = int(args[0])
    user_id = get_user_id()
    task = service.get_task_with_user_by_id(task_id, user_id)
    print_task_with_user(task)

def cmd_restore(service, args):
    if len(args) < 1:
        print("usage: restore <id>")
        return
        
    task_id = int(args[0])
    try:
        service.restore(task_id)
        print("復元しました")
    except ValueError:
        print("IDが不正です")
    except TaskNotFoundError:
        print("見つかりません")  

def format_line(tasks):
        lines = []
        lines.append(f'{"id":<3} | {"description":<12} | {"status":>7} | {"created_at":^19} | {"updated_at":^19}')
        for task in tasks:
            lines.append(
                f'{task.id:<3} | {task.description:<12} | {task.status:>7} | {task.created_at[:19]} | {task.updated_at[:19]}')
        return "\n".join(lines)  


if __name__ == "__main__":
    main()