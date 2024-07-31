from pynput import keyboard
import time
import json

log_file = "keylog.json"
current_word = ""
word_start_time = None
log_data = []

def on_press(key):
    global current_word, word_start_time, log_data
    
    timestamp = time.time()
    
    if word_start_time is None:
        word_start_time = timestamp

    try:
        char = key.char
        current_word += char
    except AttributeError:
        if key == keyboard.Key.space:
            if current_word:
                log_data.append({
                    "word": current_word,
                    "start_time": word_start_time,
                    "end_time": timestamp
                })
                current_word = ""
                word_start_time = None
        elif key == keyboard.Key.backspace:
            if current_word:
                current_word = current_word[:-1]
            log_data.append({
                "error": "backspace",
                "time": timestamp
            })

def on_release(key):
    if key == keyboard.Key.esc:
        with open(log_file, 'w') as f:
            json.dump(log_data, f)
        return False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print(f"Keylogger started. Logging to {log_file}. Press 'esc' to stop.")
listener.join()

print(f"Keylogger stopped. Data has been logged to {log_file}.")