import os
from tools.diff import generate_diff, print_diff

BASE_DIR = "workspace"

def get_full_path(path: str):
    return os.path.join(BASE_DIR, path)

# ---------------- LIST FILES ---------------- #
def list_files():
    items = []

    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            items.append(os.path.relpath(os.path.join(root, d), BASE_DIR) + "/")
        
        for f in files:
            items.append(os.path.relpath(os.path.join(root, f), BASE_DIR))

    if not items:
        return "Empty workspace"

    return "\n".join(items)

# ---------------- CREATE FILE ---------------- #
def create_file(path: str):
    full_path = get_full_path(path)

    if os.path.exists(full_path):
        return f"File already exists at {full_path}"

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("")

    return f"File created at {full_path}"

# ---------------- CREATE FOLDER ---------------- #
def create_folder(path: str):
    full_path = get_full_path(path)
    
    if os.path.exists(full_path):
        return f"Folder already exists at {full_path}"
    
    os.makedirs(full_path, exist_ok=True)
    return f"Folder created at {full_path}"

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