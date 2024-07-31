from pynput import keyboard
import time
import json
from collections import deque

class TypingLogger:
    def __init__(self, log_file="keylog.json", window_size=5):
        self.log_file = log_file
        self.log_data = []
        self.current_word = ""
        self.word_start_time = None
        self.last_key_time = None
        self.recent_keys = deque(maxlen=window_size)

    def on_press(self, key):
        timestamp = time.perf_counter()  # More precise than time.time()
        
        if self.word_start_time is None:
            self.word_start_time = timestamp

        interval = timestamp - self.last_key_time if self.last_key_time else 0
        self.last_key_time = timestamp

        try:
            char = key.char
            self.log_key_event("press", char, timestamp, interval)
            self.current_word += char
            self.recent_keys.append(char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.log_word()
                self.log_key_event("press", "space", timestamp, interval)
                self.recent_keys.append(" ")
            elif key == keyboard.Key.backspace:
                if self.current_word:
                    self.current_word = self.current_word[:-1]
                self.log_key_event("press", "backspace", timestamp, interval)
                if self.recent_keys:
                    self.recent_keys.pop()
            elif key == keyboard.Key.enter:
                self.log_word()
                self.log_key_event("press", "enter", timestamp, interval)
                self.recent_keys.clear()

    def on_release(self, key):
        if key == keyboard.Key.esc:
            self.save_log()
            return False

    def log_key_event(self, event_type, key, timestamp, interval):
        self.log_data.append({
            "type": event_type,
            "key": key,
            "time": timestamp,
            "interval": interval,
            "context": ''.join(self.recent_keys)
        })

    def log_word(self):
        if self.current_word:
            self.log_data.append({
                "type": "word",
                "word": self.current_word,
                "start_time": self.word_start_time,
                "end_time": self.last_key_time
            })
            self.current_word = ""
            self.word_start_time = None

    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log_data, f)

    def start(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            print(f"Keylogger started. Logging to {self.log_file}. Press 'esc' to stop.")
            listener.join()
        print(f"Keylogger stopped. Data has been logged to {self.log_file}.")

if __name__ == "__main__":
    logger = TypingLogger()
    logger.start()