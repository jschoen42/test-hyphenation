import sys
from pathlib import Path

import yaml
from yaml.parser import ParserError

from src.utils.trace import Trace, timeit

#  externe Liste -> settings/settings.yaml
#
#  - AlleDeutschenWoerter: https://github.com/cpos/AlleDeutschenWoerter
#  - wortliste:            https://github.com/davidak/wortliste
#  - german_words:         https://github.com/0LL13/german_words
#  - wordlist-german:      https://gist.github.com/MarvinJWendt/2f4f4154b8ae218600eb091a5706b5f4
#  - de_DE_frami:          https://github.com/LibreOffice/dictionaries/tree/master/de
#

BASE_PATH = Path(sys.argv[0]).parent
SAMPLES_DIR = BASE_PATH / "samples"
SETTING_DIR = BASE_PATH / "settings"

@timeit("import samples")
def import_samples( sample_name: str, sub_samples: list = [], language = "#" ) -> list | set:

    try:
        with open( SETTING_DIR / "settings.yaml", "r", encoding="utf-8") as file:
            settings = yaml.safe_load(file)
    except ParserError as err:
        Trace.fatal(f"settings.yaml: {err}")

    sample = settings[sample_name]
    type     = sample["type"]
    encoding = sample["encoding"]
    files    = sample["files"]

    if type == "yaml":
        words = list()
    elif type in ["dic", "text"]:
        words = set()
    else:
        Trace.fatal(f"unknown type '{type}'")

    for file in files:
        if type == "yaml":
            words.extend(import_samples_yaml(SAMPLES_DIR / language, file, sub_samples))

        elif type == "dic":
            words = words | import_samples_dictionary(SAMPLES_DIR / language / sample_name, file, encoding)

        elif type == "text":
            words = words | import_samples_text(SAMPLES_DIR / language / sample_name, file, encoding)

    Trace.info(f"{sample_name}-{type}: {len(words)} samples"  )

    if type == "yaml":
        return (sample_name, words)
    else:
        return (sample_name, sorted(words))

# YAML

def import_samples_yaml( dirpath: Path, filename: str, sub_samples: list ) -> list:
    words = []

    try:
        with open( dirpath / filename, "r", encoding="utf-8") as file:
            samples = yaml.safe_load(file)

    except OSError as err:
        Trace.error(f"{err}")
        return words

    except ParserError as err:
        Trace.fatal(f"{filename}: {err}")

    found = []
    for sub_sample in sub_samples:
        if sub_sample in samples:
            words.extend(samples[sub_sample])
            found.append(sub_sample)
        else:
            Trace.warning(f"'{filename}' unknown sub_sample '{sub_sample}'")

    Trace.info(f"'{filename}' - {found}: {len(words)} samples")
    return words

# DICTIONARY

def import_samples_dictionary( dirpath: Path, filename: str, encoding: str ) -> set:
    words = set()

    try:
        with open(dirpath / filename, "r", encoding=encoding) as file:
            for i, line in enumerate(file):
                if i==0 or len(line) == 0 or line.startswith("#") :
                    continue

                word = line.split("/")[0]
                words.add(word)

    except OSError as err:
        Trace.error(f"{err}")

    return words

# TEXT

def import_samples_text( dirpath: Path, filename: str, encoding: str ) -> set:
    words = set()

    try:
        with open(dirpath / filename, "r", encoding=encoding) as file:
            for line in file:
                line = line.strip().replace("\ufeff", "") # german_words.txt

                if len(line) == 0 or line.startswith("#"):
                    continue

                if "[Bearbeiten]" in line: # -> AlleDeutschenWoerter
                    continue

                parts = line.split(",")    # sein, war, gewesen
                for part in parts:
                    part = part.strip()
                    if len(part) == 0:
                        continue

                    words.add(part)

    except OSError as err:
        Trace.error(f"{err}")

    return words
