import json
from collections import defaultdict

def analyze_keylog(file_path):
    with open(file_path, 'r') as file:
        log_data = json.load(file)

    total_time = 0
    total_words = 0
    error_count = 0
    char_errors = defaultdict(int)
    word_errors = defaultdict(int)

    for entry in log_data:
        if "word" in entry:
            word_time = entry["end_time"] - entry["start_time"]
            total_time += word_time
            total_words += 1
            
            # Check for errors in this word
            word_error_count = sum(1 for e in log_data if e.get("error") == "backspace" and 
                                   entry["start_time"] <= e["time"] <= entry["end_time"])
            if word_error_count > 0:
                word_errors[entry["word"]] += 1
                error_count += word_error_count
                
                # Estimate which characters were likely errors
                error_chars = set(entry["word"][-(word_error_count):])
                for char in error_chars:
                    char_errors[char] += 1

    # Calculate WPM
    wpm = (total_words / (total_time / 60)) if total_time > 0 else 0

    # Calculate accuracy
    total_characters = sum(len(entry["word"]) for entry in log_data if "word" in entry)
    accuracy = ((total_characters - error_count) / total_characters) * 100 if total_characters > 0 else 100

    return {
        'wpm': wpm,
        'accuracy': accuracy,
        'error_characters': dict(char_errors),
        'error_words': dict(word_errors)
    }

# Usage
results = analyze_keylog('keylog.json')

print(f"WPM: {results['wpm']:.2f}")
print(f"Accuracy: {results['accuracy']:.2f}%")
print("Most common error characters:")
for char, count in sorted(results['error_characters'].items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  '{char}': {count} times")
print("Words with most errors:")
for word, count in sorted(results['error_words'].items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  '{word}': {count} times")