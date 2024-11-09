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

from src.hyphen import init_hyphen, get_hyphen # PyHyphen
from src.pyphen import init_pyphen, get_pyphen # Pyphon

from src.words import import_words

from src.utils.trace import Trace, Color

special_words = [
    "Fortschritt",
    "Blumentopferde",
    "Administrationsoberfläche",
    "Bedarfsanflughafen",
    "Benutzerauthentifizierungs-",
    "Bildredaktionsausschuss",
    "Blechblasinstrument",
    "Blitzeinschaltsignal",
    "Brückeneinsturz",
    "Zeichentrickfilme",
    "Zebrastreifen-",
    "Alkoholausschank",

    "Silbentrennung",
    "Universität",
    "Abenduniversität",
    "Mindestentfernung",
    "Miniaturausgabe",
    "Haustechnikraum",
    "Technik",

    "Technikraum",
    "technikraum",

    "Technikvorraum",
    "Abendstern",
    "Morgenstern",
    "Morgenthau",
    "Gastherme",
    "Funktionentheorie",
    "Gemeindebibliothek",
    "Nennwertherabsetzung",

    "Schiffahrt",

    "Baden-Württemberg"
]


################ PyHyphen - check for patch 'mode=4'

def check_patch_list():
    check_patch( import_words() )

def check_patch_special():
    check_patch( special_words )

def check_patch( words: list ):

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
        Trace.update(f"patched '{word}': '{difference[word][0]}' => '{difference[word][1]}'")

    Trace.result(f"all: {len(words)}, identical: {len(identical)}, different: {len(difference)}")

#################

# Pyphen <-> PyHyphen (without patch)
# identical: 24475, different: 1695

# Pyphen <-> PyHyphen (with patch)
# identical: 24861, different: 1309

def compare_words_list():
    words = import_words()
    compare_words( words, False )

def compare_words_special():
    words = special_words
    compare_words( words, True )

def compare_words( words: list, show_trace):

    difference = {}
    identical = {}

    # Pyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")
    init_pyphen("de_DE")

    # PyHyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen with patch...{Color.RESET}")
    init_hyphen("de_DE")

    for word in words:
        result_pyphen = get_pyphen(word, trace=show_trace)
        result_hyphen = get_hyphen(word, trace=show_trace, patch=True)
        if result_pyphen != result_hyphen:
            difference[word] = [result_pyphen, result_hyphen]
        else:
            identical[word] = result_hyphen

    for word in difference:
        Trace.info(f"'{word}': {Color.RED}{Color.BOLD}Pyphen{Color.RESET} '{difference[word][0]}', {Color.BLUE}{Color.BOLD}PyHyphen{Color.RESET} '{difference[word][1]}'")

    Trace.result(f"all: {len(words)}, identical: {len(identical)}, different: {len(difference)}")


if __name__ == "__main__":
    Trace.set( debug_mode=False, show_timestamp=False )
    Trace.action(f"Python version {sys.version}")

    # Pyphen <-> PyHyphen (with patch)
    compare_words_special()
    # compare_words_list()

    # PyHyphen
    # check_patch_special()
    # check_patch_list()
