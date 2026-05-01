import json

from agent.model import LocalModel
from agent.parser import parse_json
from tools.file_tools import create_file, create_folder, write_file, read_file, list_files, edit_file, run_command

TOOLS = {
    "create_file": create_file,
    "create_folder": create_folder,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
    "edit_file": edit_file,
    "run_command": run_command
}

TOOL_SCHEMAS = {
    "respond": ["content"],
    "create_file": ["path"],
    "create_folder": ["path"],
    "write_file": ["path", "content"],
    "read_file": ["path"],
    "list_files": [],
    "edit_file": ["path", "old", "new"],
    "run_command": ["command"]
}

SYSTEM_PROMPT = """
You are an AI coding agent.

You MUST strictly follow the rules below.

----------------------------------------
AVAILABLE TOOLS:

1. respond
   input: { "content": "text response to user" }

2. create_file
   input: { "path": "file name" }

3. create_folder
   input: { "path": "folder name" }

4. write_file
   input: { "path": "file name", "content": "text" }

5. read_file
   input: { "path": "file name" }

6. list_files
   input: {}

7. edit_file
   input: { "path": "file name", "old": "text", "new": "text" }

8. run_command
   input: { "command": "shell command" }

----------------------------------------

COMMAND RULES:
- Use run_command ONLY for safe development commands
- Examples:
  - npm create vite@latest myapp
  - npm install
  - npm run dev
  - python main.py
- NEVER run destructive commands
- NEVER delete system files
- Always assume working directory is workspace/

----------------------------------------
WORKFLOW RULES:

- ALWAYS call list_files first
- If file does not exist → create_file
- THEN write_file
- NEVER skip steps
- NEVER write to a file that does not exist

----------------------------------------
CRITICAL OUTPUT RULES (VERY IMPORTANT):

- You MUST return EXACTLY ONE JSON object
- You MUST NOT return multiple JSON objects
- You MUST NOT return any text outside JSON
- You MUST NOT explain anything
- You MUST NOT include markdown (no ```json)
- You MUST NOT suggest next steps
- You MUST NOT describe what will happen

----------------------------------------
VALID OUTPUT FORMAT:

{ "action": "create_file", "path": "test.py" }

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

Examples: 
Create file: { "action": "create_file", "path": "test.py" } 
Write file: { "action": "write_file", "path": "test.py", "content": "print('hello')" } 
Read file: { "action": "read_file", "path": "test.py" } 
List files: { "action": "list_files }
"""

class Agent:
    def __init__(self):
        self.model = LocalModel()
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
            
            parsed = parse_json(response)

            if parsed and "action" in parsed:
                print("\n\n\n" + "PARSED OUTPUT" + json.dumps(parsed, sort_keys=True) + "\n\n\n")
                
                current_signature = json.dumps(parsed, sort_keys=True)
                
                if current_signature == last_signature:
                    print("⚠️ Repeating exact same action. Stopping.")
                    return
                
                action = parsed["action"]
                # print("Parsed - ", parsed)
                print(f"🔧 Action: {action}")

                if action == "respond":
                    content = parsed.get("content", "")
                    
                    print("\n💬", content)
                    return
                
                if action == "finish":
                    print("\n✅ Task completed successfully! 🎉")
                    return
                
                if action == "edit_file":
                    print("✏️ Editing file...")
                    
                if action == "run_command":
                    command = parsed.get("command") or parsed.get("cmd")

                    if not command and "input" in parsed:
                        command = parsed["input"].get("command")

                    if not command:
                        return "❌ Missing command"

                    result = run_command(command)

                last_signature = current_signature

                if action in TOOLS:
                    allowed = TOOL_SCHEMAS[action]
                    args = {
                        k: v for k, v in parsed.items() if k in allowed
                    }

                    result = TOOLS[action](**args)
                    print("\n⚙️", result)

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