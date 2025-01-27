from typing import Any, List

from hyphen import Hyphenator # type: ignore[import-untyped] # mypy + pyright
from hyphen import dictools   # type: ignore[import-untyped] # mypy + pyright

from utils.globals   import BASE_PATH
from utils.trace     import Trace
from utils.decorator import duration

DICT_DIR = BASE_PATH / "dict"

hyphen: Hyphenator

@duration("PyHyphen init")
def init_hyphen( language: str = "de_DE" ) -> None:
    global hyphen

    dirpath = DICT_DIR
    if not dirpath.exists():
        Trace.fatal(f"PyHyphen directory '{dirpath}' not found")

    hyphen = Hyphenator(language, directory=dirpath)

def get_hyphen( word: str, patch: bool = True, trace: bool = False ) -> str :

    parts = word.split("-") # e.g. "Baden-Württemberg"

    result: List[Any] = []
    for part in parts:
        part_original = part

        if patch:
            mode = 0
            if part.istitle():
                part = part.lower()
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
        Trace.result(f"PyHyphen: {pprint_hyphen(result)}")

    return pprint_hyphen(result)

def pprint_hyphen( parts: List[Any] ) -> str:
    result = ""
    for part in parts:
        result = result + "·".join(part) + "-"

    return result[:-1]

def download_all() -> None:
    languages = dictools.LANGUAGES
    for language in languages:
        try:
            dictools.install(language, directory=DICT_DIR )
            Trace.info(f"downloading {language}")
        except Exception as _err:
            pass
