import sys
from service import CrudService
from sqlite_db import SQLiteDatabase
from repository import TaskRepository, UserRepository 
from query import TaskQueryService
from exceptions import TaskNotFoundError

def main():
    if len(sys.argv) < 2:
        print("input command")
        return
    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("input command")
            return
        task = sys.argv[2]
        service.add(task)
        print("追加しました")  
    elif command == "delete":
        if len(sys.argv) < 3:
            print("input id")
            return
        try:
            task = int(sys.argv[2])
            service.delete(task)
            print("削除しました")
        except ValueError:
            print("IDが不正です")
        except TaskNotFoundError:
            print("見つかりません")
    elif command == "update":
        if len(sys.argv) < 4:
            print("引数が必要です")
            return
        new_task = sys.argv[3]
        try:
            task_id = int(sys.argv[2])
            service.update(task_id, new_task)
            print("更新しました")
        except ValueError:
            print("IDが不正です")    
        except TaskNotFoundError:
            print("見つかりません")
        
    elif command == "list":
        if len(sys.argv) == 2:
            try:
                result = service.list_tasks()
                print(format_line(result))
            except TaskNotFoundError:
                print("見つかりません")
            return    
        status = sys.argv[2]
        if len(sys.argv) == 3:
            try:
                result = service.list_sts(status)
                print(result)
            except TaskNotFoundError:
                print("見つかりません")
            except ValueError:
                print("ステータスが不正です")
    elif command in ("done", "in-progress", "to-do"):
        if len(sys.argv) < 3:
            print("引数が必要です")
            return       
        task_id = int(sys.argv[2])
        try:
            service.mark(command, task_id)
            print("ステータスが変更されました。")
        except ValueError:
            print("ステータスが不正です")
        except TaskNotFoundError:
                print("見つかりません")
    else:
        print("error command")

def format_line(tasks):
        lines = []
        lines.append(f'{"id":<3} | {"description":<12} | {"status":>7} | {"createdAt":^19} | {"updatedAt":^19}')
        for task in tasks:
            lines.append(
                f'{task.id:<3} | {task.description:<12} | {task.status:>7} | {task.createdAt[:19]} | {task.updatedAt[:19]}')
        return "\n".join(lines)  

db = SQLiteDatabase()

task_repo = TaskRepository(db)
user_repo = UserRepository(db)
query_repo = TaskQueryService(db)
service = CrudService(task_repo, user_repo, query_repo)

if __name__ == "__main__":
    main()