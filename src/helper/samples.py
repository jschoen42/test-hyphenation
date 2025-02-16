from typing import Any, List, Set, Tuple
from pathlib import Path

import yaml
from yaml.parser import ParserError

from utils.globals   import BASE_PATH
from utils.trace     import Trace
from utils.decorator import duration

#  externe Liste -> settings/settings.yaml
#
#  - AlleDeutschenWoerter: https://github.com/cpos/AlleDeutschenWoerter
#  - wortliste:            https://github.com/davidak/wortliste
#  - german_words:         https://github.com/0LL13/german_words
#  - wordlist-german:      https://gist.github.com/MarvinJWendt/2f4f4154b8ae218600eb091a5706b5f4
#  - de_DE_frami:          https://github.com/LibreOffice/dictionaries/tree/master/de
#

SAMPLES_DIR = BASE_PATH / "samples"
SETTING_DIR = BASE_PATH / "settings"

@duration("import samples")
def import_samples( sample_name: str, sub_samples: List[str] | None = None, language: str = "#" ) -> Tuple[str, List[str] | Set[str]]:

    if sub_samples is None:
        sub_samples = []

    settings: Any = {}
    try:
        with open( SETTING_DIR / "settings.yaml", "r", encoding="utf-8") as file:
            settings = yaml.safe_load(file)
    except ParserError as err:
        Trace.fatal(f"settings.yaml: {err}")

    sample   = settings[sample_name]
    type     = sample["type"]
    encoding = sample["encoding"]
    files    = sample["files"]

    if type == "yaml":
        words_yaml: List[str] = list()
        for file in files:
            words_yaml.extend(import_samples_yaml(SAMPLES_DIR / language, str(file), sub_samples))

        Trace.info(f"{sample_name}-{type}: {len(words_yaml)} samples"  )
        return (sample_name, words_yaml)

    elif type == "dic":
        words_dict: Set[str] = set()
        for file in files:
            words_dict = words_dict | import_samples_dictionary(SAMPLES_DIR / language / sample_name, str(file), encoding)

        Trace.info(f"{sample_name}-{type}: {len(words_dict)} samples"  )
        return (sample_name, sorted(words_dict))

    elif type == "text":
        words_text: Set[str] = set()
        for file in files:
            words_text = words_text | import_samples_text(SAMPLES_DIR / language / sample_name, str(file), encoding)

        Trace.info(f"{sample_name}-{type}: {len(words_text)} samples"  )
        return (sample_name, sorted(words_text))

    else:
        Trace.fatal(f"unknown type '{type}'")
        return (sample_name, [])

# YAML

def import_samples_yaml( dirpath: Path, filename: str, sub_samples: List[str] ) -> List[str]:
    words: List[str] = []

    samples: Any = {}
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

def import_samples_dictionary( dirpath: Path, filename: str, encoding: str ) -> set[str]:
    words = set()

    try:
        with open(dirpath / filename, "r", encoding=encoding) as file:
            for i, line in enumerate(file):
                line = line.strip()
                if i==0 or len(line) == 0 or line.startswith("#") :
                    continue

                word = line.split("/")[0]
                words.add(word)

    except OSError as err:
        Trace.error(f"{err}")

    return words

# TEXT

def import_samples_text( dirpath: Path, filename: str, encoding: str ) -> set[str]:
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
