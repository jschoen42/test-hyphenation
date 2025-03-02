"""
    © Jürgen Schoenemeyer, 02.03.2025 19:37

    src/helper/pyhyphen.py

    PyHyphen 4.0.4
    https://pypi.org/project/PyHyphen/
    https://github.com/dr-leo/PyHyphen

    https://github.com/LibreOffice/dictionaries/blob/master/de/hyph_de_DE.dic

    PUBLIC:
     - init_pyhypen( language: str = "de_DE" ) -> None
     - get_pyhypen( word:str, patch: bool = True, trace: bool = False ) -> str

    PRIVATE:
     - format_word( parts: List[Any] ) -> str
     - download_pyhypen_all() -> None
"""
from __future__ import annotations

from typing import Any, List

from hyphen import Hyphenator  # type: ignore[import-untyped]

from utils.decorator import duration
from utils.globals import BASE_PATH
from utils.trace import Trace

DICT_DIR = BASE_PATH / "dict"

hyphen: Hyphenator

@duration("PyHyphen init")
def init_pyhyphen( language: str = "de_DE" ) -> None:
    global hyphen

    dirpath = DICT_DIR
    if not dirpath.exists():
        Trace.fatal(f"PyHyphen directory '{dirpath}' not found")

    hyphen = Hyphenator(language, directory=dirpath)

def get_pyhyphen( word: str, patch: bool = True, trace: bool = False ) -> str :

    parts = word.split("-") # e.g. "Baden-Württemberg"

    result: List[Any] = []
    for part in parts:
        part_original = part

        if patch:
            mode = 0
            if part.istitle():
                part = part.lower()  # noqa: PLW2901
                mode = 4

            res = hyphen.syllables(part)
            if len(res) == 0:
                res = [part_original]

            elif mode == 4:
                res[0] = res[0].title()

        else:
            res = hyphen.syllables(part)
            if len(res) == 0:
                res = [part_original]

        result.append(res)

    if trace:
        Trace.result(f"PyHyphen: {format_word(result)}")

    return format_word(result)

def format_word( parts: List[Any] ) -> str:
    result = ""
    for part in parts:
        result = result + "·".join(part) + "-"

    return result[:-1]

# def download_pyhyphen_all() -> None:
#     languages = dictools.LANGUAGES
#     for language in languages:
#         try:
#             dictools.install(language, directory=DICT_DIR )
#             Trace.info(f"downloading {language}")
#         except Exception as err:
#             Trace.error(f"{err}")
