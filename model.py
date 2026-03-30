from datetime import datetime
class TaskProperty:
    
    def __init__(self, id: int, description: str, status: str, user_id: str, createdAt: str, updatedAt: str, deletedAt):
        self.id = id
        self.description = self.check_description(description)
        self.status = status
        self.user_id = user_id
        self.createdAt = createdAt
        self.updatedAt = (
            updatedAt if updatedAt is not None
            else datetime.now().isoformat()
            )
        self.deletedAt = deletedAt
    def update_description(self, new_description: str):
        desc = self.check_description(new_description)
        changed = self.description != desc
        if changed:
            self.description = desc
        return changed

    def change_status(self, new_status: str):
        sts = self.check_status(new_status)
        changed = self.status != sts
        if changed:
            self.status = sts
        return changed  
    def replace(self, new_description: str, new_status: str):
        #バリデーションチェック
        desc = self.check_description(new_description)
        sts = self.check_status(new_status)
        #OKなら代入
        self.description = desc
        self.status = sts
    #APIレスポンス対応
    def to_dict(self):
        return {
        "id": self.id,
        "description": self.description,
        "status": self.status,
        "createdAt": self.createdAt,
        "updatedAt": self.updatedAt,
    } 
    def patch(self, description: str | None = None, status: str | None = None): 
        changed = False
        
        if description is not None:
            changed = changed or self.update_description(description)
        if status is not None:           
            changed = changed or self.change_status(status)

        return changed
    
    def check_description(self, description):
        if not description or not description.strip():
            raise ValueError
        if len(description) > 200:
            raise ValueError("too long")
        return description.strip()
    def check_status(self, status):
        valid_status = {"to-do", "in-progress", "done"}
        if status not in valid_status:
            raise ValueError
        return status