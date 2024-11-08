# PyHyphen

from hyphen import Hyphenator
from hyphen import dictools

from src.utils.trace import Trace, timeit

DATA_DIR = "./_tests"

hyphen = None

@timeit("PyHyphen init")
def init_hyphen( language: str = "de_DE" ):
    global hyphen

    hyphen = Hyphenator(language, directory=DATA_DIR)

def get_hyphen( word: str, patch: bool = True, trace: bool = False ):
    if patch:
        mode = 0
        if word.istitle():
            word = word.lower()
            mode = 4

        result = hyphen.syllables(word)
        if mode == 4:
            result[0] = result[0].title()
    else:
        result = hyphen.syllables(word)

    if len(result) == 0: # very short words
        result = [word]

    if trace:
        Trace.result(f"{"-".join(result)}")

    return result


def download_all():
    languages = dictools.LANGUAGES
    for language in languages:
        try:
            dictools.install(language, directory=DATA_DIR )
            Trace.info(f"downloading {language}")
        except Exception as _err:
            pass