from google import genai
from config import API_KEY
import threading
import time
import sys

class GeminiModel:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)

    def _thinking_animation(self, stop_event):
        start_time = time.time()
        spinner = ["|", "/", "-", "\\"]
        i = 0

        while not stop_event.is_set():
            elapsed = time.time() - start_time
            sys.stdout.write(f"\r🤖 Thinking {spinner[i % len(spinner)]} {elapsed:.1f}s")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

        sys.stdout.write("\r" + " " * 60 + "\r")

    def generate(self, prompt):
        stop_event = threading.Event()
        thread = threading.Thread(target=self._thinking_animation, args=(stop_event,))
        thread.start()

        response = self.client.models.generate_content(
            model="models/gemma-4-31b-it",
            contents=prompt
        )

        stop_event.set()
        thread.join()

        return response.text