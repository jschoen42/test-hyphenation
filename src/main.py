# .venv/Scripts/activate
# python src/main.py

import sys

from typing import Any, Dict, List
from result import is_err #, is_ok

from main.hyphen import init_hyphen, get_hyphen # PyHyphen
from main.pyphen import init_pyphen, get_pyphen # Pyphon

from helper.samples import import_samples

from utils.globals   import BASE_PATH
from utils.trace     import Trace, Color
from utils.decorator import duration
from utils.files     import write_file

RESULT_DIR = BASE_PATH / "results"

##############################################################
# check_samples("PyHyphen", "de_DE", "samples", ["test_patch, special, dashes, upper"])
# check_samples("PyHyphen", "de_DE", "AlleDeutschenWoerter")
# check_samples("PyHyphen", "de_DE", "wortliste")
# check_samples("PyHyphen", "de_DE", "german_words")
# check_samples("PyHyphen", "de_DE", "de_DE_frami")
#
# check_samples("Pyphen", "de_DE", "samples", ["test_patch, special, dashes, upper"])
# check_samples("Pyphen", "de_DE", "AlleDeutschenWoerter")
# check_samples("Pyphen", "de_DE", "wortliste")
# check_samples("Pyphen", "de_DE", "german_words")
# check_samples("Pyphen", "de_DE", "de_DE_frami")
##############################################################

def check_samples(package_name: str, language: str, set_name: str, sub_set: List[Any] = [], trace: bool = False ) -> None:

    set_name, samples = import_samples(set_name, sub_set, language)

    results: List[Any] = []
    if package_name == "Pyphen":
        results = test_Pyphen(samples, language, trace)

    elif package_name == "PyHyphen":
        results = test_PyHyphen(samples, language, trace)

    else:
        Trace.fatal(f"unknown package name '{package_name}'")

    filename = f"{package_name}_COMPLETE_{set_name}.json"
    timestamp = (set_name == "samples")

    ret = write_file(RESULT_DIR / language / set_name / filename, results, filename_timestamp=timestamp)
    if is_err(ret):
        Trace.error(f"Error: {ret.err_value}")

    Trace.result(f"results: {len(results)}")

@duration("Pyphen test all")
def test_Pyphen(words: Dict[str, str], language: str, trace:bool = True) -> Dict[str, str]:
    Trace.action(f"{Color.BLUE}{Color.BOLD}Pyphen ...{Color.RESET}")
    init_pyphen(language)

    result = {}
    for word in words:
        result[word] = get_pyphen(word, trace = trace)

    return result

@duration("PyHyphen test all")
def test_PyHyphen(words: Dict[str, str], language: str, trace:bool = True) -> Dict[str, str]:
    Trace.action(f"{Color.BLUE}{Color.BOLD}PyHyphen with patch ...{Color.RESET}")
    init_hyphen(language)

    result: Dict[str, str] = {}
    for word in words:
        result[word] = get_hyphen(word, trace = trace)

    return result

##############################################################
# PyHyphen - check for patch 'mode=4'
#
# compare_samples( "de_DE", "samples", ["test_patch", "special", "dashes", "upper"] )
# compare_samples( "de_DE", "AlleDeutschenWoerter")
# compare_samples( "de_DE", "wortliste")
# compare_samples( "de_DE", "german_words")
# compare_samples( "de_DE", "de_DE_frami")
##############################################################

def check_patch_samples( language: str, set_name: str, sub_set: List[str] = [], trace: bool = False ) -> None:

    set_name, samples = import_samples(set_name, sub_set, language)

    difference: Dict[str, List[str]] = {}
    identical: Dict[str, str] = {}

    init_hyphen(language)

    for word in samples:
        result_no_patch = get_hyphen(word, trace = trace, patch = False)
        result_patch = get_hyphen(word, trace = trace, patch=True)
        if result_no_patch != result_patch:
            difference[word] = [result_no_patch, result_patch]
        else:
            identical[word] = result_no_patch

    if trace:
        for word in difference:
            Trace.update(f"patched '{word}': '{difference[word][0]}' => '{difference[word][1]}'")

    filename = f"PyHyphen_PATCH_{set_name}.json"
    timestamp = (set_name == "samples")

    ret = write_file(RESULT_DIR / language / set_name / filename, difference, filename_timestamp=timestamp)
    if is_err(ret):
        Trace.error(f"Error: {ret.err_value}")

    Trace.result(f"all: {len(samples)}, identical: {len(identical)}, different: {len(difference)}")

##############################################################
#
# Pyphen <-> PyHyphen (with patch)
#
# compare_samples( "de_DE", "samples", ["test_patch", "special", "dashes", "upper"] )
# compare_samples( "de_DE", "AlleDeutschenWoerter")
# compare_samples( "de_DE", "wortliste")
# compare_samples( "de_DE", "german_words")
# compare_samples( "de_DE", "de_DE_frami")
#
##############################################################

def compare_samples( language: str, set_name: str, sub_set: List[str] = [], trace: bool = False ) -> None:

    set_name, samples = import_samples(set_name, sub_set, language)

    difference: Dict[str, List[str]] = {}
    identical: Dict[str, str] = {}

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

    filename = f"Pyphen-PyHyphen_DIFF_{set_name}.json"
    timestamp = (set_name == "samples")

    ret = write_file(RESULT_DIR / language / set_name / filename, difference, filename_timestamp=timestamp )
    if is_err(ret):
        Trace.error(f"Error: {ret.err_value}")

    Trace.result(f"all: {len(samples)}, identical: {len(identical)}, different: {len(difference)}")


def main() -> None:
    # PyHyphen - Patch (on, off)

    check_patch_samples("de_DE", "samples", ["test_patch", "dashes", "upper", "special", "corrected", "wrong"])
    check_patch_samples("de_DE", "AlleDeutschenWoerter")
    check_patch_samples("de_DE", "wortliste")
    check_patch_samples("de_DE", "german_words")
    check_patch_samples("de_DE", "de_DE_frami")
    check_patch_samples("de_DE", "wordlist-german")

    # PyHyphen (mit Patch)

    # check_samples("PyHyphen", "de_DE", "samples", ["test_patch", "dashes", "upper", "special", "corrected", "wrong"], trace=True)
    # check_samples("PyHyphen", "de_DE", "AlleDeutschenWoerter")
    # check_samples("PyHyphen", "de_DE", "wortliste")
    # check_samples("PyHyphen", "de_DE", "german_words")
    # check_samples("PyHyphen", "de_DE", "de_DE_frami")
    # check_samples("PyHyphen", "de_DE", "wordlist-german")

    # Pyphen

    # check_samples("Pyphen", "de_DE", "samples", ["test_patch", "dashes", "upper", "special", "corrected", "wrong"], trace=True)
    # check_samples("Pyphen", "de_DE", "AlleDeutschenWoerter")
    # check_samples("Pyphen", "de_DE", "wortliste")
    # check_samples("Pyphen", "de_DE", "german_words")
    # check_samples("Pyphen", "de_DE", "de_DE_frami")
    # check_samples("Pyphen", "de_DE", "wordlist-german")

    # PyHyphen (with patch) <-> Pyphen

    # compare_samples("de_DE", "samples", ["test_patch", "dashes", "upper", "special", "corrected", "wrong"])
    # compare_samples("de_DE", "AlleDeutschenWoerter")
    # compare_samples("de_DE", "wortliste")
    # compare_samples("de_DE", "german_words")
    # compare_samples("de_DE", "de_DE_frami")
    # compare_samples("de_DE", "wordlist-german")

if __name__ == "__main__":
    Trace.set( debug_mode=False, timezone=False )
    Trace.action(f"Python version {sys.version}")

    try:
        main()
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit()
