from src.utils.trace import Trace, timeit

from pathlib import Path

@timeit("read dic")
def parse_dic( path: Path, filename: str ) -> dict:
    result = {}

    with open(path / filename, "r", encoding="ISO-8859-1") as file:
        lines = file.read().splitlines()

        for line in lines:
            if "ISO8859-1" in line:
                continue

            if "COMPOUNDLEFTHYPHENMIN" in line:
                continue

            if "COMPOUNDRIGHTHYPHENMIN" in line:
                continue

            if line == "":
                continue

            if line[0] == "#":
                continue

            if "NOHYPHEN" in line:
                break

            word = line.strip()
            result[word] = [word.replace("1", "")]

    return result
