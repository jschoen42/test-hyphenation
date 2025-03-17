"""
    © Jürgen Schoenemeyer, 17.03.2025 18:10

    src/helper/samples.py

    samples -> settings/settings.yaml
     - AlleDeutschenWoerter: https://github.com/cpos/AlleDeutschenWoerter
     - wortliste:            https://github.com/davidak/wortliste
     - german_words:         https://github.com/0LL13/german_words
     - wordlist-german:      https://gist.github.com/MarvinJWendt/2f4f4154b8ae218600eb091a5706b5f4
     - de_DE_frami:          https://github.com/LibreOffice/dictionaries/tree/master/de

    PUBLIC:
     - import_samples( sample_name: str, sub_samples: List[str] | None = None, language: str = "#" ) -> Tuple[str, List[str] | Set[str]]

    PRIVATE:
     - import_samples_yaml( dirpath: Path, filename: str, sub_samples: List[str] ) -> List[str]
     - import_samples_dictionary( dirpath: Path, filename: str, encoding: str ) -> Set[str]
     - import_samples_text( dirpath: Path, filename: str, encoding: str ) -> Set[str]
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Set, Tuple

import yaml

from yaml.parser import ParserError

from utils.decorator import duration
from utils.globals import BASE_PATH
from utils.trace import Trace

if TYPE_CHECKING:
    from pathlib import Path

SETTING_DIR = BASE_PATH / "settings"
SAMPLES_DIR = BASE_PATH / "samples"

# PUBLIC

@duration("import samples")
def import_samples( sample_name: str, sub_samples: List[str] | None = None, language: str = "#" ) -> Tuple[str, List[str] | Set[str]]:

    if sub_samples is None:
        sub_samples = []

    settings: Any = {}
    try:
        with (SETTING_DIR / "settings.yaml").open(mode="r", encoding="utf-8") as file:
            settings = yaml.safe_load(file)
    except ParserError as err:
        Trace.fatal(f"settings.yaml: {err}")

    sample   = settings[sample_name]
    type     = sample["type"]
    encoding = sample["encoding"]
    files    = sample["files"]

    if type == "yaml":
        words_yaml: List[str] = []
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

# PRIVATE

# YAML (samples.yaml)

def import_samples_yaml( dirpath: Path, filename: str, sub_samples: List[str] ) -> List[str]:
    words: List[str] = []

    samples: Any = {}
    try:
        with (dirpath / filename).open(mode="r", encoding="utf-8") as file:
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

# DICTIONARY (de_DE_frami)

def import_samples_dictionary( dirpath: Path, filename: str, encoding: str ) -> Set[str]:
    words = set()

    try:
        with (dirpath / filename).open(mode="r", encoding=encoding) as file:
            for i, line in enumerate(file):
                line = line.strip()  # noqa: PLW2901
                if i==0 or len(line) == 0 or line.startswith("#") :
                    continue

                word = line.split("/")[0]
                words.add(word)

    except OSError as err:
        Trace.error(f"{err}")

    return words

# TEXT (AlleDeutschenWoerter, german_words, wordlist-german, wortliste)

def import_samples_text( dirpath: Path, filename: str, encoding: str ) -> Set[str]:
    words = set()

    try:
        with (dirpath / filename).open(mode="r", encoding=encoding) as file:
            for line in file:
                line = line.strip().replace("\ufeff", "") # german_words.txt  # noqa: PLW2901

                if len(line) == 0 or line.startswith("#"):
                    continue

                if "[Bearbeiten]" in line: # -> AlleDeutschenWoerter
                    continue

                parts = line.split(",")    # sein, war, gewesen
                for part in parts:
                    part = part.strip()  # noqa: PLW2901
                    if len(part) == 0:
                        continue

                    words.add(part)

    except OSError as err:
        Trace.error(f"{err}")

    return words
