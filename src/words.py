from pathlib import Path

from src.utils.trace import Trace, timeit

BASE_PATH = "./material/AlleDeutschenWoerter"

word_lists = [
    "Adjektive/Adjektive.txt",
    "Substantive/substantiv_singular_der.txt",
    " Substantive/substantiv_singular_die.txt",
    "Substantive/substantiv_singular_das.txt",
    "Verben/Verben_regelmaeßig.txt",
    "Verben/Verben_unregelmaeßig_Infinitiv.txt",
]

@timeit("import words")
def import_words():
    words = []
    for word_list in word_lists:
        with open(Path(BASE_PATH) / word_list, "r", encoding="utf-8") as f:
            for line in f:
                if "[Bearbeiten]" not in line:
                    words.append(line.strip().title())

    Trace.result("import_words", len(words))

    return words

