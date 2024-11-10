# .venv\Scripts\activate
# python main.py
#

import sys
from datetime import datetime
from pathlib import Path

from result import is_err #, is_ok

from src.hyphen import init_hyphen, get_hyphen # PyHyphen
from src.pyphen import init_pyphen, get_pyphen # Pyphon

from src.samples import import_samples

from src.utils.trace import Trace, Color, timeit
from src.utils.files import write_file

test_sample = [
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

RESULT_DIR = Path(sys.argv[0]).parent / "results"

##############################################################
# check_samples("PyHyphen", "de_DE")
# check_samples("PyHyphen", "de_DE", "AlleDeutschenWoerter")
# check_samples("PyHyphen", "de_DE", "wortliste")
# check_samples("PyHyphen", "de_DE", "german_words")
# check_samples("PyHyphen", "de_DE", "de_DE_frami")
#
# check_samples("Pyphen", "de_DE")
# check_samples("Pyphen", "de_DE", "AlleDeutschenWoerter")
# check_samples("Pyphen", "de_DE", "wortliste")
# check_samples("Pyphen", "de_DE", "german_words")
# check_samples("Pyphen", "de_DE", "de_DE_frami")
##############################################################

def check_sample(package_name, language):
    if package_name == "Pyphen":
        result = test_Pyphen(test_sample, language)

    elif package_name == "PyHyphen":
        result = test_PyHyphen(test_sample, language)

    else:
        Trace.fatal(f"unknown package name '{package_name}'")

    return result

def check_samples(package_name, language, samples_name  ):

    set_name, samples = import_samples(samples_name)

    # dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # filename = f"{package_name}-{set_name}-{dt}.json"
    filename = f"{package_name}-{set_name}.json"

    if package_name == "Pyphen":
        results = test_Pyphen(samples, language, trace=False)

    elif package_name == "PyHyphen":
        results = test_PyHyphen(samples, language, trace=False)

    else:
        Trace.fatal(f"unknown package name '{package_name}'")

    Trace.result(f"results: {len(results)}")

    ret = write_file(RESULT_DIR, filename, results )
    if is_err(ret):
        Trace.error(f"Error: {ret.err_value}")

@timeit("Pyphen test all")
def test_Pyphen(words: dict, language: str, trace:bool = True) -> list:
    Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")
    init_pyphen(language)

    result = {}
    for word in words:
        result[word] = get_pyphen(word, trace = trace)

    return result

@timeit("PyHyphen test all")
def test_PyHyphen(words: dict, language: str, trace:bool = True) -> list:
    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen with patch ...{Color.RESET}")
    init_hyphen(language)

    result = {}
    for word in words:
        result[word] = get_hyphen(word, trace = trace)

    return result

##############################################################
# PyHyphen - check for patch 'mode=4'
#
# check_patch_sample()
# compare_samples( "de_DE", "AlleDeutschenWoerter")
# compare_samples( "de_DE", "wortliste")
# compare_samples( "de_DE", "german_words")
# compare_samples( "de_DE", "de_DE_frami")
##############################################################

def check_patch_sample( language: str ):
    check_patch( "", test_sample, language, trace=False )

def check_patch_samples( language: str, set_name: str  ):
    set_name, samples = import_samples(set_name)

    check_patch( set_name, samples, language, trace=False )

def check_patch( set_name: str, words: list, language: str, trace:bool = True ):

    difference = {}
    identical = {}

    init_hyphen(language)

    for word in words:
        result_no_patch = get_hyphen(word, trace = trace, patch = False)
        result_patch = get_hyphen(word, trace = trace, patch=True)
        if result_no_patch != result_patch:
            difference[word] = [result_no_patch, result_patch]
        else:
            identical[word] = result_no_patch

    if trace:
        for word in difference:
            Trace.update(f"patched '{word}': '{difference[word][0]}' => '{difference[word][1]}'")

    if set_name != "":
        # dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # filename = f"PyHypen-PATCH-{set_name}-{dt}.json"
        filename = f"PyHypen-PATCH-{set_name}.json"

        ret = write_file(RESULT_DIR, filename, difference )
        if is_err(ret):
            Trace.error(f"Error: {ret.err_value}")

    Trace.result(f"all: {len(words)}, identical: {len(identical)}, different: {len(difference)}")

##############################################################
#
# Pyphen <-> PyHyphen (with patch)
#
# compare_sample( "de_DE" )
# compare_samples( "de_DE", "AlleDeutschenWoerter")
# compare_samples( "de_DE", "wortliste")
# compare_samples( "de_DE", "german_words")
# compare_samples( "de_DE", "de_DE_frami")
#
##############################################################

def compare_sample( language ):
    samples = test_sample
    compare_words( "", samples, language, True )

def compare_samples( language, set_name ):
    set_name, samples = import_samples(set_name)

    compare_words( set_name, samples, language, False )

def compare_words( set_name, samples: list, language: str, trace: bool):

    difference = {}
    identical = {}

    # Pyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")
    init_pyphen(language)

    # PyHyphen

    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen with patch...{Color.RESET}")
    init_hyphen(language)

    for word in samples:
        result_pyphen = get_pyphen(word, trace = trace)
        result_hyphen = get_hyphen(word, trace = trace, patch=True)
        if result_pyphen != result_hyphen:
            difference[word] = [result_pyphen, result_hyphen]
        else:
            identical[word] = result_hyphen

    if trace:
        for word in difference:
            Trace.info(f"'{word}': {Color.RED}{Color.BOLD}Pyphen{Color.RESET} '{difference[word][0]}', {Color.BLUE}{Color.BOLD}PyHyphen{Color.RESET} '{difference[word][1]}'")

    if set_name != "":
        # dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # filename = f"PyHypen-Python-differences{set_name}-{dt}.json"
        filename = f"PyHypen-Python-differences{set_name}.json"

        ret = write_file(RESULT_DIR, filename, difference )
        if is_err(ret):
            Trace.error(f"Error: {ret.err_value}")

    Trace.result(f"all: {len(samples)}, identical: {len(identical)}, different: {len(difference)}")


if __name__ == "__main__":
    Trace.set( debug_mode=False, show_timestamp=False )
    Trace.action(f"Python version {sys.version}")

    # PyHyphen - Patch (on, off)
    check_patch_sample("de_DE")
    check_patch_samples("de_DE", "AlleDeutschenWoerter")
    check_patch_samples("de_DE", "wortliste")
    check_patch_samples("de_DE", "german_words")
    check_patch_samples("de_DE", "de_DE_frami")

    # PyHyphen (mit Patch)
    check_sample("PyHyphen", "de_DE")
    check_samples("PyHyphen", "de_DE", "AlleDeutschenWoerter")
    check_samples("PyHyphen", "de_DE", "wortliste")
    check_samples("PyHyphen", "de_DE", "german_words")
    check_samples("PyHyphen", "de_DE", "de_DE_frami")

    # Pyphen
    check_sample("Pyphen", "de_DE")
    check_samples("Pyphen", "de_DE", "AlleDeutschenWoerter")
    check_samples("Pyphen", "de_DE", "wortliste")
    check_samples("Pyphen", "de_DE", "german_words")
    check_samples("Pyphen", "de_DE", "de_DE_frami")

    # PyHyphen (with patch) <-> Pyphen
    compare_sample("de_DE" )
    compare_samples("de_DE", "AlleDeutschenWoerter")
    compare_samples("de_DE", "wortliste")
    compare_samples("de_DE", "german_words")
    compare_samples("de_DE", "de_DE_frami")

