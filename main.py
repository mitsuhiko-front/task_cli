import sys
from service import CrudService
from repository import TaskRepository, UserRepository 
from query import TaskQueryService
from sqlite_db import SQLiteDatabase
from exceptions import TaskNotFoundError

def get_service():
    db = SQLiteDatabase()
    db._create_tables()
    task_repo = TaskRepository(db)
    user_repo = UserRepository(db)
    query_repo = TaskQueryService(db)
    return CrudService(task_repo, user_repo, query_repo)


def print_task(task):
    print(f"[{task.id}] {task.description} ({task.status})")


def main():
    if len(sys.argv) < 2:
        print("usage: <command> [args]")
        return
    service = get_service()
    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "add": cmd_add,
        "delete": cmd_delete,
        "update": cmd_update,
        "list": cmd_list,
    }

    if command not in commands:
        print("error command")
        return

    commands[command](service, args)

def cmd_add(service, args):    
    if len(args) < 3:
        print("usage: add <description>")
        return

    description = args[0]
    service.add(description)
    print("追加しました")  
def cmd_delete(service, args): 
    if len(sys.argv) < 3:
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
    if len(sys.argv) < 3:
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
    tasks = service.list_tasks()
    print(tasks)

def cmd_restore(service, args):
    if len(sys.argv) < 3:
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
        lines.append(f'{"id":<3} | {"description":<12} | {"status":>7} | {"createdAt":^19} | {"updatedAt":^19}')
        for task in tasks:
            lines.append(
                f'{task.id:<3} | {task.description:<12} | {task.status:>7} | {task.createdAt[:19]} | {task.updatedAt[:19]}')
        return "\n".join(lines)  


if __name__ == "__main__":
    main()