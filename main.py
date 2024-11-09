# .venv\Scripts\activate
# python main.py
#
# Mark Liang Standford University 1983
# https://www.tug.org/docs/liang/liang-thesis.pdf
#
# >>>> https://hyphenation.org/
#
# https://tex.stackexchange.com/questions/398491/how-does-texs-hyphenation-algorithm-work
#
# https://github.com/dr-leo/PyHyphen/
#
# https://github.com/Kozea/Pyphen
#
# https://github.com/mnater/Hyphenopoly
#
# https://ctan.org/tex-archive/language/hyphenation/dehyph
#
# https://github.com/voikko/libreoffice-voikko/blob/master/oxt/pythonpath/Hyphenator.py

# hunspell implementation
# https://github.com/hunspell/hyphen/blob/master/README.compound

# LibreOffice
# C:\Program Files\LibreOffice\share\extensions\dict-de
# https://github.com/libreoffice
# https://github.com/hunspell/hyphen/blob/master/hyphen.c
# https://github.com/voikko/libreoffice-voikko/blob/master/oxt/pythonpath/HyphenatedWord.py
# -> com.sun.star.linguistic2 - XHyphenatedWord
# https://api.libreoffice.org/docs/idl//ref/interfacecom_1_1sun_1_1star_1_1linguistic2_1_1XHyphenatedWord.html#details
# D:\downloads\core-master\linguistic\source\hyphdsp.cxx

import sys
from pathlib import Path

from src.hyphen import init_hyphen, get_hyphen # PyHyphen
from src.pyphen import init_pyphen, get_pyphen # Pyphon

from src.words import import_words

from src.utils.trace import Trace, Color, timeit
from src.utils.util import export_json

from dic import parse_dic

                                      # PyHyphen                          <-> Pyphon
special_words = [
    # "Fort-schritt",                   # Forts-chritt                      <-> Fort-s-chritt
    # "Blumen-topf-erde",
    # "Ad-ministrations-ober-fläche",
    # "Bedarfs-an-flug-hafen",          # Be-darfsan-flug-ha-fen            <-> Be-da-rfs-an-flug-ha-fen
    # "Benutzer-authenti-fizierungs-",  # Be-nut-zerau-then-ti-fi-zie-rungs <-> Be-nut-zer-au-then-ti-fi-zie-rungs
    # "Bild-re-daktions-aus-schuss",
    # "Blech-blas-in-strument",
    # "Blitz-ein-schalt-signal",
    # "Brücken-ein-sturz",
    # "Zeichen-trick-filme",
    # "Zebra-streifen-",
    # "Alkohol-aus-schank",

    # "Silben-tren-nung",
    # "Universität",
    # "Abenduniversität",
    # "Mindestentfernung",
    # "Miniaturausgabe",
    # "Haustechnikraum",
    # "Technik",

    # "Technikraum",
    # "technikraum",

    # "Technikvorraum",
    "Fortschritt",
   "Abendstern",
   "Morgenstern",
   "Morgenthau",
   "Gastherme",
   # "Funktionentheorie",
   # "Gemeindebibliothek",
   "Nennwertherabsetzung",
    #"Schiffahrt"
    "Baden-Württemberg"


]


################

def check_patch_list():
    words = import_words()
    check_patch( words )

def check_patch_special():
    words = special_words
    check_patch( words )

def check_patch( words: list ):

    # PyHyphen

    difference = {}
    identical = {}

    init_hyphen("de_DE")
    for word in words:
        result_no_patch = get_hyphen(word, trace=False, patch=False)
        result_patch = get_hyphen(word, trace=False, patch=True)
        if result_no_patch != result_patch:
            difference[word] = [result_no_patch, result_patch]
        else:
            identical[word] = result_no_patch

    for word in difference:
        Trace.error(f"patch is working: {word}: {difference[word][0]} -> {difference[word][1]}")

    Trace.result(f"identical: {len(identical)}, different: {len(difference)}")



#################

def test_words_list():
    words = import_words()
    test_words( words, "list" )

def test_words_special():
    words = special_words
    test_words( words, "special" )

def test_words( words: list, type: str):

    # PyHyphen without patch

    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen without patch...{Color.RESET}")
    init_hyphen("de_DE")

    results = {}
    for word in words:
        result = get_hyphen(word, trace=True, patch=False)
        results[result] = word

    # Trace.fatal(results)

    # PyHyphen with patch

    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen with patch...{Color.RESET}")
    init_hyphen("de_DE")

    count = 0
    for word in words:
        result = get_hyphen(word, trace=True, patch=True)
        if result not in results:
            count += 1
            # Trace.error(f"patch is working: {word} -> {result}")

    Trace.result(f"patch: {count}")

    # Pyphen

    # Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")
    # init_pyphen("de_DE")
    # for word in words:
    #     _result = get_pyphen(word, trace=(type == "special"))


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

def test_big():

    # leider ist "hyph_de_DE.dic" nicht für den Test verwendbar, Substantive sind klein geschrieben !!!

    words = parse_dic( Path("."), "hyph_de_DE.dic")
    Trace.info(f"{len(words)} words")

    ### PyHyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen ...{Color.RESET}")

    init_hyphen("de_DE")

    @timeit("PyHyphen test")
    def test_hyphen():
        global result

        for _word, result in words.items():
            res = get_hyphen(result[0], patch = True)
            result.append("-".join(res))

    test_hyphen()

    # ### Pyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")

    init_pyphen("de_DE")

    @timeit("Pyphon test")
    def test_pypen():
        global result

        for _word, result in words.items():
            res = get_pyphen(result[0])
            result.append(res)

    test_pypen()

    equal = 0
    different = 0

    for _word, result in words.items():
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

    test_words_special()
    # test_big()
    # test_words_special()
    # test_words_list()
    # check_patch_special()
    # check_patch_list()
