import json

FILE = "task_cli.json"

def read_expenses():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def write_expenses(expenses):
    with open(FILE, "w") as f:
        json.dump(expenses, f, indent=2)