import json
class JsonRepository:    
    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                data = json.load(f)
            return [
                TaskProperty(
                    d["id"],
                    d["description"],
                    d["status"],
                    d["created_at"],
                    d["updated_at"]
                )
            for d in data
        ]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    def save_tasks(self, tasks):
        with open("tasks.json", "w") as f: 
            json.dump([t.to_dict() for t in tasks], f, indent=4)      
