import json
from collections import defaultdict
from spellchecker import SpellChecker
import numpy as np

class TypingAnalyzer:
    def __init__(self, log_file="keylog.json"):
        self.log_file = log_file
        self.spell = SpellChecker()
        self.log_data = self.load_log()
        self.words = []
        self.word_times = []
        self.char_timings = defaultdict(list)
        self.results = {}

    def load_log(self):
        with open(self.log_file, 'r') as file:
            return json.load(file)

    def analyze(self):
        self.process_log_data()
        self.calculate_wpm()
        self.calculate_accuracy()
        self.analyze_misspellings()
        self.analyze_slow_keys()
        return self.results

    def process_log_data(self):
        current_word = ""
        word_start_time = None

        for entry in self.log_data:
            if entry["type"] == "press":
                if entry["key"] == "space" or entry["key"] == "enter":
                    if current_word:
                        self.words.append(current_word)
                        word_time = entry["time"] - word_start_time
                        self.word_times.append(word_time)
                        current_word = ""
                        word_start_time = None
                elif entry["key"] == "backspace":
                    if current_word:
                        current_word = current_word[:-1]
                else:
                    if word_start_time is None:
                        word_start_time = entry["time"]
                    current_word += entry["key"]
                    self.char_timings[entry["key"]].append(entry["interval"])

        # Add the last word if there's no space at the end
        if current_word:
            self.words.append(current_word)
            self.word_times.append(entry["time"] - word_start_time)

    def calculate_wpm(self):
        if not self.word_times:
            self.results["wpm"] = 0
            return

        avg_time_per_word = np.mean(self.word_times)
        words_per_minute = 60 / avg_time_per_word
        self.results["wpm"] = words_per_minute

    def calculate_accuracy(self):
        correct_words = sum(1 for word in self.words if word in self.spell)
        total_words = len(self.words)
        self.results["accuracy"] = (correct_words / total_words) * 100 if total_words > 0 else 100

    def analyze_misspellings(self):
        misspelled_words = []
        for word in self.words:
            if word not in self.spell:
                correct_word = self.spell.correction(word)
                highlighted_word = self.highlight_misspelling(word, correct_word)
                misspelled_words.append((word, highlighted_word, correct_word))
        self.results["misspelled_words"] = misspelled_words

    def highlight_misspelling(self, misspelled, correct):
        highlighted = ""
        for i, (c1, c2) in enumerate(zip(misspelled, correct)):
            if c1 != c2:
                highlighted += f"[{c1}]"
            else:
                highlighted += c1
        if len(misspelled) > len(correct):
            highlighted += f"[{''.join(misspelled[len(correct):])}]"
        elif len(misspelled) < len(correct):
            highlighted += f"[+{''.join(correct[len(misspelled):])}]"
        return highlighted

    def analyze_slow_keys(self):
        avg_timings = {char: np.mean(timings) for char, timings in self.char_timings.items()}
        slowest_keys = sorted(avg_timings.items(), key=lambda x: x[1], reverse=True)[:10]
        self.results["slowest_keys"] = slowest_keys

if __name__ == "__main__":
    analyzer = TypingAnalyzer()
    results = analyzer.analyze()

    print(f"1. WPM: {results['wpm']:.2f}")
    print(f"2. Accuracy: {results['accuracy']:.2f}%")
    
    print("\n3. Misspelled words:")
    for misspelled, highlighted, correct in results['misspelled_words']:
        print(f"   {misspelled} -> {highlighted} (Correct: {correct})")
    
    print("\n5. Slowest keys (average time in seconds):")
    for char, avg_time in results['slowest_keys']:
        print(f"   '{char}': {avg_time:.3f}s")