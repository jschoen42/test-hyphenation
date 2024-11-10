import sys
from pathlib import Path

from src.utils.trace import Trace, timeit

# Testsets:
# AlleDeutschenWoerter
# wortliste
# german_words

BASE_PATH = Path(sys.argv[0]).parent / "samples"

word_lists = {
    "AlleDeutschenWoerter": {
        "encoding": "utf-8",
        "files": [
            "Adjektive/Adjektive.txt",
            "Substantive/substantiv_singular_der.txt",
            "Substantive/substantiv_singular_die.txt",
            "Substantive/substantiv_singular_das.txt",
            "Verben/Verben_regelmaeßig.txt",
            "Verben/Verben_unregelmaeßig_Infinitiv.txt",
        ]
    },
    "wortliste": {
        "encoding": "utf-8",
        "files": [
            "wortliste.txt"
        ],
    },
    "german_words": {
        "encoding": "utf-8",
        "files": [
            "german_words.txt"
        ]
    },
    "de_DE_frami": {
        "encoding": "cp1252",
        "files":  [
            "de_DE_frami.dic"
        ],
    }
}

@timeit("import samples")
def import_samples( test_set: str ):
    words = set()

    dirpath = BASE_PATH / test_set

    infos = word_lists[test_set]
    encoding = infos["encoding"]
    files    = infos["files"]

    for file in files:
        suffix = Path(file).suffix

        with open(dirpath / file, "r", encoding=encoding) as file:
            for i, line in enumerate(file):
                line = line.strip().replace("\ufeff", "") # german_words.txt

                if len(line) == 0:
                    continue

                if line.startswith("#"):
                    continue

                if suffix == ".dic":
                    if i==0:
                        continue

                    word = line.split("/")[0]
                    words.add(word)

                else:
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
