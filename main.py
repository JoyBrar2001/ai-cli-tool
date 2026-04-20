from google import genai
import json
from tools import create_file, write_file, read_file

client = genai.Client(api_key="AIzaSyC9DmNDog9cjHvgYuQdA5H5w1pW-DryZeM")

TOOLS = {
    "create_file": create_file,
    "write_file": write_file,
    "read_file": read_file
}

SYSTEM_PROMPT = """
You are an AI coding agent.

You have access to these tools:

1. create_file
   - input: { "path": "file name" }

2. write_file
   - input: { "path": "file name", "content": "text" }

3. read_file
   - input: { "path": "file name" }

RULES:
- If a tool is needed → return ONLY JSON
- Do NOT include explanation
- Do NOT include markdown
- Always return valid JSON

Examples:

Create file:
{
  "action": "create_file",
  "path": "test.py"
}

Write file:
{
  "action": "write_file",
  "path": "test.py",
  "content": "print('hello')"
}

Read file:
{
  "action": "read_file",
  "path": "test.py"
}
"""

def call_gemini(user_input):
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=SYSTEM_PROMPT + "\nUser: " + user_input
    )
    return response.text


def try_parse_json(text):
    try:
        return json.loads(text)
    except:
        return None


def main():
    print("🤖 Geminix CLI started. Type 'exit' to quit.\n")

    while True:
        user_input = input("> ")

        if user_input.lower() == "exit":
            break

        conversation = user_input

        for step in range(5):  # limit steps to avoid infinite loops
            response = call_gemini(conversation)
            print(response)
            parsed = try_parse_json(response)
            print(parsed)

            if parsed and "action" in parsed:
                action = parsed["action"]

                if action in TOOLS:
                    try:
                        result = TOOLS[action](**{k: v for k, v in parsed.items() if k != "action"})
                        print(f"⚙️ {result}")

                        # Feed result back to model
                        conversation += f"\nTool result: {result}\nWhat should be done next?"

                    except Exception as e:
                        print(f"❌ Tool error: {str(e)}")
                        break
                else:
                    print("❌ Unknown tool")
                    break
            else:
                print(response)
                break

if __name__ == "__main__":
    main()