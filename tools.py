import os

BASE_DIR = "workspace"

def get_full_path(path: str):
    return os.path.join(BASE_DIR, path)


def create_file(path: str):
    full_path = get_full_path(path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("")

    return f"File created at {full_path}"


def write_file(path: str, content: str):
    full_path = get_full_path(path)

    if not os.path.exists(full_path):
        return "Error: File does not exist. Create it first."

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written at {full_path}"


def read_file(path: str):
    full_path = get_full_path(path)

    if not os.path.exists(full_path):
        return "Error: File does not exist."

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()