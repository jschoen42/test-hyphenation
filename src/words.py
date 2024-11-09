from pathlib import Path

from src.utils.trace import Trace, timeit

BASE_PATH = "./tests/AlleDeutschenWoerter"

word_lists = [
    "Adjektive/Adjektive.txt",
    "Substantive/substantiv_singular_der.txt",
    "Substantive/substantiv_singular_die.txt",
    "Substantive/substantiv_singular_das.txt",
    "Verben/Verben_regelmaeßig.txt",
    "Verben/Verben_unregelmaeßig_Infinitiv.txt",
]

@timeit("import words")
def import_words():
    words = []
    duplicate = []

    for word_list in word_lists:
        with open(Path(BASE_PATH) / word_list, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == "":
                    continue

                if "[Bearbeiten]" in line:
                    continue

                parts = line.split(",") # sein, war, gewesen
                for part in parts:
                    word = part.strip()

                    if word in words:
                        duplicate.append(word)
                        # Trace.error(f"duplicate word '{word}' ({word_list})")

                    else:
                        words.append(part.strip()) # .title())

    Trace.info(f"words {len(words)}, duplicates {len(duplicate)}"  )

    return words
