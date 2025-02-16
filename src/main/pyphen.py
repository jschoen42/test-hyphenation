import pyphen  # type: ignore[import-untyped]

from utils.globals   import BASE_PATH
from utils.trace     import Trace
from utils.decorator import duration

DICT_DIR = BASE_PATH / "dict"

pyphen_dic: pyphen.Pyphen

@duration("Pyphen init")
def init_pyphen( language: str="de_DE" ) -> None:
    global pyphen_dic

    dirpath = DICT_DIR
    if not dirpath.exists():
        Trace.fatal(f"Pyphen directory '{dirpath}' not found")

    filepath = dirpath / f"hyph_{language}.dic"
    if not filepath.exists():
        Trace.fatal(f"Pyphen dictionary '{filepath}' not found")

    pyphen_dic = pyphen.Pyphen(filename=filepath)

def get_pyphen( word:str, trace: bool = False ) -> str:
    global pyphen_dic

    parts = word.split("-") # e.g. "Baden-Württemberg"

    result = []
    for part in parts:
        result.append(pyphen_dic.inserted(part, "·"))

    if trace:
        Trace.result(f"Pyphen:   {"-".join(result)}")

    return f"{"-".join(result)}"
