# Pyphen

from pathlib import Path

import pyphen

from src.utils.trace import Trace, timeit

DICT_DIR = "./dict"

pyphen_dic = None

@timeit("Pyphon init")
def init_pyphen( language: str="de_DE" ):
    global pyphen_dic

    filepath = Path(DICT_DIR) / f"hyph_{language}.dic"
    if not filepath.exists():
        Trace.fatal(f"Pyphen dictionary '{filepath}' not found")

    pyphen_dic = pyphen.Pyphen(filename=filepath)

def get_pyphen( word:str, trace: bool = False ):
    global pyphen_dic

    parts = word.split("-") # e.g. "Baden-Württemberg"

    result = []
    for part in parts:
        result.append(pyphen_dic.inserted(part, "~"))

    if trace:
        Trace.result(f"{"-".join(result)}")

    return f"{"-".join(result)}"
