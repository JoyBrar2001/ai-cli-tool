import json

from agent.model import LocalModel
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
    "respond": ["content"],
    "create_file": ["path"],
    "create_folder": ["path"],
    "write_file": ["path", "content"],
    "read_file": ["path"],
    "list_files": [],
    "edit_file": ["path", "old", "new"]
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

----------------------------------------
INVALID OUTPUT (NEVER DO THIS):

❌ Multiple JSON:
{ "action": "create_file" }
{ "action": "write_file" }

❌ JSON + explanation:
{ "action": "create_file" }
This will create a file.

❌ Markdown:
```json
{ "action": "create_file" }
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