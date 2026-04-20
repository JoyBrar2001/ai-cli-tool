from google import genai
import json
from tools import create_file, write_file, read_file, list_files
import threading
import time
import sys

# ---------------- UX ---------------- #
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

# ---------------- MODEL ---------------- #
client = genai.Client(api_key="AIzaSyBWgvq4ljA2WO7Iil-UvyMC0gAcdhLtneU")  # ⚠️ replace with env var

# ---------------- TOOLS ---------------- #
TOOLS = {
    "create_file": create_file,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files
}

TOOL_SCHEMAS = {
    "create_file": ["path"],
    "write_file": ["path", "content"],
    "read_file": ["path"],
    "list_files": []
}

# ---------------- PROMPT ---------------- #
SYSTEM_PROMPT = """
You are an AI coding agent.

TOOLS:

1. create_file → { "path": "file name" }
2. write_file → { "path": "file name", "content": "text" }
3. read_file → { "path": "file name" }
4. list_files → {}

TASK COMPLETION RULES:
- If task is fully complete → return:
  { "action": "finish" }

- DO NOT repeat the same action if it already succeeded
- DO NOT recreate existing files
- After writing correct content → FINISH immediately
- Prefer minimal steps

IMPORTANT:
- Before creating/writing → call list_files
- Avoid duplicates

STRICT TOOL RULES:
- create_file → only path
- write_file → path + content
- read_file → only path
- list_files → no params

Return ONLY JSON when using tools.
"""

# ---------------- GEMINI CALL ---------------- #
def call_gemini(user_input):
    stop_event = threading.Event()
    thread = threading.Thread(target=thinking_animation, args=(stop_event,))
    
    thread.start()

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=SYSTEM_PROMPT + "\nUser: " + user_input
    )

    stop_event.set()
    thread.join()

    return response.text

# ---------------- JSON PARSER ---------------- #
def try_parse_json(text):
    try:
        text = text.strip()

        # Extract JSON inside markdown
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and part.endswith("}"):
                    return json.loads(part)

        # Extract first {...} block if extra text exists
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start:end+1])

        return None
    except Exception:
        return None

# ---------------- MAIN LOOP ---------------- #
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
        last_action = None

        for step in range(1, MAX_STEPS + 1):
            print(f"\n🧠 Step {step}/{MAX_STEPS}")
            print("-" * 40)

            response = call_gemini(conversation)
            print(response)

            parsed = try_parse_json(response)

            if parsed and "action" in parsed:
                action = parsed["action"]
                print(f"🔧 Action: {action}")

                # ✅ FINISH HANDLER
                if action == "finish":
                    print("\n✅ Task completed successfully! 🎉")
                    completed = True
                    break

                # ✅ LOOP GUARD
                if action == last_action:
                    print("⚠️ Repeating same action. Stopping to avoid loop.")
                    completed = True
                    break

                last_action = action

                # ✅ TOOL EXECUTION
                if action in TOOLS:
                    try:
                        allowed_args = TOOL_SCHEMAS[action]
                        filtered_args = {
                            k: v for k, v in parsed.items() if k in allowed_args
                        }

                        result = TOOLS[action](**filtered_args)
                        print(f"⚙️ {result}")

                        # ✅ Better feedback loop
                        conversation += f"""
User goal: {user_input}

Last action: {action}
Result: {result}

What should be done next?
If task is complete, return:
{{ "action": "finish" }}
"""

                    except Exception as e:
                        print(f"❌ Tool error: {str(e)}")
                        completed = True
                        break
                else:
                    print("❌ Unknown tool")
                    completed = True
                    break
            else:
                print("\n💬 Response:")
                print(response)
                completed = True
                break

        if not completed:
            print("\n⚠️ Request too long.")
            print("👉 Please break it down into smaller steps.\n")

        print("=" * 60)


if __name__ == "__main__":
    main()