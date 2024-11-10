import sys
from pathlib import Path

from src.utils.trace import Trace, timeit

# Testsets:
# AlleDeutschenWoerter
# wortliste
# german_words

BASE_PATH = Path(sys.argv[0]).parent / "samples"

word_lists = {
    "AlleDeutschenWoerter": [
        "Adjektive/Adjektive.txt",
        "Substantive/substantiv_singular_der.txt",
        "Substantive/substantiv_singular_die.txt",
        "Substantive/substantiv_singular_das.txt",
        "Verben/Verben_regelmaeßig.txt",
        "Verben/Verben_unregelmaeßig_Infinitiv.txt",
    ],
    "wortliste": [
        "wortliste.txt"
    ],
    "german_words": [
        "german_words.txt"
    ]
}

@timeit("import samples")
def import_samples( test_set: str ):
    words = set()

    dirpath = BASE_PATH / test_set

    for word_list in word_lists[test_set]:
        with open(dirpath / word_list, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip().replace("\ufeff", "") # german_words.txt

                if len(line) == 0:
                    continue

                # -> AlleDeutschenWoerter

                if "[Bearbeiten]" in line:
                    continue

                parts = line.split(",") # sein, war, gewesen
                for part in parts:
                    part = part.strip()
                    if len(part) == 0:
                        continue

                    words.add(part) #.title())

    Trace.info(f"{test_set}: words {len(words)}"  )
    return (test_set, sorted(words))
