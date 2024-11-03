# .venv-3.12\Scripts\activate
# python main.py
#
# https://github.com/dr-leo/PyHyphen/
#
# https://github.com/Kozea/Pyphen
#
# https://github.com/mnater/Hyphenopoly
#
# https://ctan.org/tex-archive/language/hyphenation/dehyph
#

# Beispiel "Fortschritt" -> "Fort-s-chritt" mit Tex Algorithmus
# in deutscher .dic steht aber zusätzlich "fort1schritt" (compound)
# PyHyphen => ['Forts', 'chritt']
# Pyphen   => ['Fortschritt']
#  -> wird von Python Paketen nicht ausgewertet, aber von LibreOffice

import sys
from pathlib import Path

from src.utils.trace import Trace, timeit
from src.utils.util import export_json

from dic import parse_dic

                                      # PyHyphen                          <-> Python
words = [
    "Fort-schritt",                   # Forts-chritt                      <-> Fort-s-chritt
    "Blumen-topf-erde",
    "Ad-ministrations-ober-fläche",
    "Bedarfs-an-flug-hafen",          # Be-darfsan-flug-ha-fen            <-> Be-da-rfs-an-flug-ha-fen
    "Benutzer-authenti-fizierungs-",  # Be-nut-zerau-then-ti-fi-zie-rungs <-> Be-nut-zer-au-then-ti-fi-zie-rungs
    "Bild-re-daktions-aus-schuss",
    "Blech-blas-in-strument",
    "Blitz-ein-schalt-signal",        # Blitzein-schalt-si-gnal           <-> Blitz-ein-schalt-si-gnal
    "Brücken-ein-sturz",
    "Zeichen-trick-filme",
    "Zebra-streifen-",
    "Alkohol-aus-schank",

    "Silben-tren-nung",
]

##################

from hyphen import Hyphenator
from hyphen import dictools

DATA_DIR = "./data"

hyphon = None

@timeit("PyHyphen init")
def init_hypen( language: str = "de_DE" ):
    global hyphon

    hyphon = Hyphenator(language, directory=DATA_DIR)

def test_hyphen( word:str ):
    result = hyphon.syllables(word)
    Trace.result(f"{"-".join(result)}")

    # trennungen = hyphon.pairs(word)
    # silben = hyphon.syllables(word)
    # wrap = hyphon.wrap(word, 10)

def download_all():
    languages = dictools.LANGUAGES
    for language in languages:
        try:
            dictools.install(language, directory=DATA_DIR )
            Trace.info(f"downloading {language}")
        except Exception as e:
            pass

################

import pyphen

pyphen_dic = None

@timeit("Python init")
def init_pyphen( language: str="de_DE" ):
    global pyphen_dic

    pyphen_dic = pyphen.Pyphen(lang=language)

def test_pyphen( word:str ):
    global pyphen_dic

    result = pyphen_dic.inserted(word) # .split("-")
    Trace.result(f"{result}")

#################

def main():

    ### PyHyphen

    init_hypen("de_DE")
    for word in words:
        test_hyphen(word.replace("-",""))

    ### Pyphen

    init_pyphen("de_DE")
    for word in words:
        test_pyphen(word.replace("-",""))


################# PyHyphen und Pyphen: alle Wörter aus 'hyph_de_DE.dic' als Test
#
# Basiert auf TeX - https://ctan.org/tex-archive/language/hyphenation/dehyph
#
# Ergebnis:
#   - generell viele Unterschiede (insg. 69090)
#      - identisch:   46237
#      - verschieden: 22853
#
#   - PyHyphen: kurze Wörter (ab, mit, hin, Weg, ...) => ""
#

def test():
    words = parse_dic( Path("."), "hyph_de_DE.dic")
    Trace.info(f"{len(words)} words")

    ### PyHyphen

    init_hypen("de_DE")

    for word, result in words.items():
        res = hyphon.syllables(result[0])
        result.append("-".join(res))

    ### Pyphen

    init_pyphen("de_DE")

    for word, result in words.items():
        res = pyphen_dic.inserted(result[0])
        result.append(res)

    equal = 0
    different = 0

    for word, result in words.items():
        if result[1] == result[2]:
            equal += 1
        else:
            result.append("different")
            different += 1

    # json dump

    export_json( Path("./result"), "result.json", words)

    Trace.result(f"equal: {equal}, different: {different}")


if __name__ == "__main__":
    Trace.set( debug_mode=False, show_timestamp=True )
    Trace.action(f"Python version {sys.version}")
    test()
