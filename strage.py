import json
import os

def save_data(filename: str, data) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data(filename: str, default_value):
    if not os.path.exists(filename):
        return default_value
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_value