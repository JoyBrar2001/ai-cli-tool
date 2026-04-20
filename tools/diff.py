import difflib

def generate_diff(old_content: str, new_content: str):
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="before",
        tofile="after",
        lineterm=""
    )

    return "".join(diff)

def print_diff(diff_text: str):
    if not diff_text:
        print("✅ No changes")
        return

    print("\n📄 Diff Preview:\n")

    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            print(f"\033[92m{line}\033[0m")  # green
        elif line.startswith("-") and not line.startswith("---"):
            print(f"\033[91m{line}\033[0m")  # red
        else:
            print(line)