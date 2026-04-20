from google import genai
import json
from tools import create_file, write_file, read_file
import threading
import time
import sys

def thinking_animation(stop_event):
    start_time = time.time()
    spinner = ["|", "/", "-", "\\"]
    i = 0

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        sys.stdout.write(
            f"\r🤖 Thinking {spinner[i % len(spinner)]} {elapsed:.1f}s"
        )
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write("\r" + " " * 60 + "\r")
    
def print_logo():
    logo = r"""
   ____                         
  / ___| ___ _ __ ___  (_)_ __ (_)\ \/ /
 | |  _ / _ \ '_ ` _ \ | | '_ \| | \  /
 | |_| |  __/ | | | | || | | | | | /  \
  \____|\___|_| |_| |_||_|_| |_|_|/ /\ \

            ⚡ GeminiX CLI Agent ⚡
    """
    print(logo)

client = genai.Client(api_key="AIzaSyBWgvq4ljA2WO7Iil-UvyMC0gAcdhLtneU")

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

STRICT TOOL RULES:

- create_file ONLY accepts: path
- write_file ONLY accepts: path, content
- read_file ONLY accepts: path

DO NOT include extra fields.

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
    stop_event = threading.Event()
    thread = threading.Thread(target=thinking_animation, args=(stop_event,))
    
    thread.start()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=SYSTEM_PROMPT + "\nUser: " + user_input
    )

    stop_event.set()
    thread.join()

    return response.text


def try_parse_json(text):
    try:
        text = text.strip()

        # Remove ```json or ``` wrappers
        if text.startswith("```"):
            text = text.split("```")[1]  # remove first ```
            text = text.replace("json", "", 1).strip()
            text = text.replace("```", "").strip()

        return json.loads(text)
    except Exception as e:
        return None


def main():
    print_logo()
    print("Type 'exit' to quit.\n")
    print("=" * 60)

    MAX_STEPS = 10

    while True:
        user_input = input("\n> ")

        if user_input.lower() == "exit":
            print("\n👋 Exiting GeminiX...\n")
            break

        conversation = user_input
        completed = False

        for step in range(1, MAX_STEPS + 1):
            print(f"\n🧠 Step {step}/{MAX_STEPS}")
            print("-" * 40)

            response = call_gemini(conversation)
            print(response)
            parsed = try_parse_json(response)

            if parsed and "action" in parsed:
                action = parsed["action"]
                print(f"🔧 Action: {action}")
                
                if action == "finish":
                    print("\n✅ Task completed successfully!")
                    completed = True
                    break

                if action in TOOLS:
                    try:
                        result = TOOLS[action](**{k: v for k, v in parsed.items() if k != "action"})
                        print(f"⚙️ {result}")

                        conversation += f"\nTool result: {result}\nWhat should be done next?"

                    except Exception as e:
                        print(f"❌ Tool error: {str(e)}")
                        break
                else:
                    print("❌ Unknown tool")
                    break
            else:
                print("\n💬 Response:")
                print(response)
                completed = True
                break

        # 🚨 If max steps reached and not completed
        if not completed:
            print("\n⚠️ Request too long.")
            print("👉 Please break it down into smaller steps.\n")

        print("=" * 60)
        

if __name__ == "__main__":
    main()