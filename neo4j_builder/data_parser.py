import json

def load_data(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)