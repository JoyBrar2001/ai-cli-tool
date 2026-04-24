import json

from agent.model import GeminiModel
from agent.parser import parse_json
from tools.file_tools import create_file, create_folder, write_file, read_file, list_files, edit_file

TOOLS = {
    "create_file": create_file,
    "create_folder": create_folder,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
    "edit_file": edit_file
}

TOOL_SCHEMAS = {
    "create_file": ["path"],
    "create_folder": ["path"],
    "write_file": ["path", "content"],
    "read_file": ["path"],
    "list_files": [],
    "edit_file": ["path", "old", "new"]
}

SYSTEM_PROMPT = """ 
You are an AI coding agent. 

You have access to these tools: 

1. create_file - input: { "path": "file name" } 
2. create_folder - input: { "path": "folder name" }
3. write_file - input: { "path": "file name", "content": "text" } 
4. read_file - input: { "path": "file name" } 
5. list_files - input: {} 
6. edit_file - input: { "path": "file name", "old": "text to replace", "new": "replacement text" }

EDITING RULES:
- Prefer edit_file instead of write_file when modifying existing files
- Use read_file first to understand content before editing
- Only modify necessary parts of the file
- Do NOT overwrite entire file unless explicitly required

IMPORTANT: 
- You MUST return ONLY ONE action at a time
- NEVER return multiple JSON objects
- After each action, wait for the next instruction
- Before creating or writing files, you SHOULD call list_files to check existing files 
- Avoid creating duplicate files 
- Use list_files to understand project structure 

RULES: 
- If a tool is needed → return ONLY JSON 
- Do NOT include explanation 
- Do NOT include markdown 
- Always return valid JSON 

STRICT TOOL RULES: 
- create_file ONLY accepts: path 
- write_file ONLY accepts: path, content 
- read_file ONLY accepts: path DO NOT include extra fields. 

Examples: 
Create file: { "action": "create_file", "path": "test.py" } 
Write file: { "action": "write_file", "path": "test.py", "content": "print('hello')" } 
Read file: { "action": "read_file", "path": "test.py" } 
List files: { "action": "list_files }
"""

class Agent:
    def __init__(self):
        self.model = GeminiModel()
        self.max_steps = 10

    def run(self, user_input):
        conversation = user_input
        last_signature = None

        for step in range(1, self.max_steps + 1):
            print(f"\n🧠 Step {step}/{self.max_steps}")
            print("-" * 40)

            response = self.model.generate(
                SYSTEM_PROMPT + "\nUser: " + conversation
            )

            print(response)

            parsed = parse_json(response)

            if parsed and "action" in parsed:
                current_signature = json.dumps(parsed, sort_keys=True)
                
                if current_signature == last_signature:
                    print("⚠️ Repeating exact same action. Stopping.")
                    return
                
                action = parsed["action"]
                print("Parsed - ", parsed)
                print(f"🔧 Action: {action}")

                if action == "finish":
                    print("\n✅ Task completed successfully! 🎉")
                    return
                
                if action == "edit_file":
                    print("✏️ Editing file...")

                last_signature = current_signature

                if action in TOOLS:
                    allowed = TOOL_SCHEMAS[action]
                    args = {k: v for k, v in parsed.items() if k in allowed}

                    result = TOOLS[action](**args)
                    print(f"⚙️ {result}")

                    conversation += f"""
User goal: {user_input}

Last action: {action}
Result: {result}

If done → return finish
"""
                else:
                    print("❌ Unknown tool")
                    return
            else:
                print("💬", response)
                return

        print("\n⚠️ Request too long. Break it down.")