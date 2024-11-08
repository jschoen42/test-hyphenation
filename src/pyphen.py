# Pyphen

import pyphen

from src.utils.trace import Trace, timeit

pyphen_dic = None

@timeit("Pyphon init")
def init_pyphen( language: str="de_DE" ):
    global pyphen_dic

    pyphen_dic = pyphen.Pyphen(lang=language)

def get_pyphen( word:str, trace: bool = False ):
    global pyphen_dic

    result = pyphen_dic.inserted(word) # .split("-")

    if trace:
        Trace.result(f"{result}")

    return result
