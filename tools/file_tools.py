import os
from tools.diff import generate_diff, print_diff

BASE_DIR = "workspace"

def get_full_path(path: str):
    return os.path.join(BASE_DIR, path)

# ---------------- LIST FILES ---------------- #
def list_files():
    file_list = []

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, BASE_DIR)
            file_list.append(relative_path)

    if not file_list:
        return "No files found."

    return "\n".join(file_list)

# ---------------- CREATE FILE ---------------- #
def create_file(path: str):
    full_path = get_full_path(path)

    if os.path.exists(full_path):
        return f"File already exists at {full_path}"

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        pass

    return f"File created at {full_path}"

# ---------------- WRITE FILE ---------------- #
def write_file(path: str, content: str):
    full_path = get_full_path(path)

    if not os.path.exists(full_path):
        return "Error: File does not exist. Create it first."

    with open(full_path, "r", encoding="utf-8") as f:
        old_content = f.read()

    diff = generate_diff(old_content, content)

    print_diff(diff)   # 👈 SHOW DIFF

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written at {full_path}"

# ---------------- READ FILE ---------------- #
def read_file(path: str):
    full_path = get_full_path(path)

    if not os.path.exists(full_path):
        return "Error: File does not exist."

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
    
def edit_file(path: str, old: str, new: str):
    full_path = get_full_path(path)

    if not os.path.exists(full_path):
        return "Error: File does not exist."

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    if old not in content:
        return "Error: target text not found."

    updated_content = content.replace(old, new, 1)

    diff = generate_diff(content, updated_content)
    print_diff(diff)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return f"Edited file at {full_path}"