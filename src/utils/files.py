"""
    (c) Jürgen Schoenemeyer, 10.11.2024

    error channel -> rustedpy/result

    PUBLIC:
    result = get_timestamp(filepath: Path | str) -> Result[float, str]:
    result = set_timestamp(filepath: Path | str, timestamp: float) -> Result[str, str]:

    result = read_file(path: Path | str, filename: str, encoding: str="utf-8" ) -> Result[str, str]
    result = write_file(path: Path | str, filename: str, data: any, encoding: str="utf-8", create_dir: bool = True) -> Result[str, str]:

    from result import is_err, is_ok

    if is_err(result):
        Trace.error(f"Error: {result.err_value}")
    else:
        data = result.ok_value

    supported types
     - .txt
     - .json
     - .xml

"""

import os
import sys

from datetime import datetime

import xml.etree.ElementTree as ET

if "orjson" in sys.modules:
    import orjson # optional
else:
    import json

from pathlib import Path
from result import Result, Ok, Err

from src.utils.trace import Trace

TIMESTAMP = '%Y-%m-%d_%H-%M-%S'

def get_timestamp(filepath: Path | str) -> Result[float, str]:
    """
    ---
    get timestamp of a file

    Parameters
     - filepath: Path or str

    Result [rustedpy]
     - Ok: timestamp as float
     - Err: errortext as str
    """

    if not filepath.exists():
        err = "'{filepath}' does not exist"
        Trace.error(f"{err}")
        return Err(err)

    try:
        ret = os.path.getmtime(Path(filepath))
    except OSError as err:
        Trace.error(f"{err}")
        return Err(f"{err}")

    return Ok(ret)

def set_timestamp(filepath: Path | str, timestamp: int|float) -> Result[str, str]:
    """
    ---
    set timestamp of a file

    Parameters
     - filepath: Path or str
     - timestamp: float

    Result [rustedpy]
     - Ok: -
     - Err: errortext as str
    """

    if not filepath.exists():
        err = "'{filepath}' does not exist"
        Trace.error(f"{err}")
        return Err(err)

    try:
        os.utime(Path(filepath), times = (timestamp, timestamp)) # atime and mtime
    except OSError as err:
        Trace.error(f"set_timestamp: {err}")

    return Ok(())

def read_file(dirpath: Path | str, filename: str, encoding: str="utf-8") -> Result[str, str]:
    """
    ---
    read file (text, json, xml)

    Parameters
     - dirpath: Path or str
     - filename: str - supported extentions: '.txt', '.json', '.xml'
     - encoding: str - used only for '.txt'

    Result [rustedpy]
     - Ok: text as str
     - Err: errortext as str
    """

    # 1. type check

    suffix  = Path(filename).suffix

    if suffix == ".txt":
        type = "text"

    elif suffix == ".json":
        type = "json"

    elif suffix == ".xml":
        type = "xml"

    else:
        return Err(f"Type '{suffix}' is not supported")

    # 2. directory check

    dirpath = Path(dirpath)
    if not dirpath.exists():
        return Err(f"DirNotFoundError: '{dirpath}'")

    # 3. file check + deserialization

    filepath = dirpath / filename
    if not filepath.exists():
        return Err(f"FileNotFoundError: '{filepath}'")

    try:
        with open(filepath, "r", encoding=encoding) as f:
            text = f.read()
    except OSError as err:
        return Err(f"{err}")

    if type == "text":
        return Ok(text)

    elif type == "json":
        if "orjson" in sys.modules:
            try:
                data = orjson.loads(text)
            except orjson.JSONDecodeError as err:
                return Err(f"JSONDecodeError: {filepath} => {err}")
            return Ok(data)
        else:
            try:
                data = json.loads(text)
            except json.JSONDecodeError as err:
                return Err(f"JSONDecodeError: {filepath} => {err}")
            return Ok(data)

    elif type == "xml":
        try:
            data = ET.fromstring(text)
        except ET.ParseError as err:
            return Err(f"ParseError: {err}")
        return Ok(data)


def write_file(dirpath: Path | str, filename: str, data: any, filename_timestamp: bool = False, timestamp: int|float = 0, encoding: str="utf-8", newline: str="\n" , create_dir: bool = True) -> Result[str, str]:
    """
    ---
    write file (text, json, xml)

    Parameters
     - dirpath: Path or str
     - filename: str - supported extentions: '.txt', '.json', '.xml'
     - filename_timestamp: bool - add to filename a timestamp
     - timestamp: float - timestamp in sec
     - encoding: str - used only for '.txt'
     - newline: str - "\\n" or "\\r\\n"
     - create_dir: bool - create directory if not exists (default: True)

    Result [rustedpy]
     - Ok: -
     - Err: errortext as str

    Infos
     - using orjson for '.json' files
     - the identical check is only content based, newline char is ignored
    """

    suffix = Path(filename).suffix
    stem = Path(filename).stem

    if filename_timestamp:
        filename = f"{stem}_{datetime.now().strftime(TIMESTAMP)}{suffix}"

    # 1. type check + serialization

    if suffix in [".txt", ".csv"]:
        if not isinstance(data, str):
            return Err(f'write_file \'{suffix}\': "{str(data)[:50]} …" is not a string')
        else:
            text = data

    elif suffix == ".json":
        if not isinstance(data, str):
            if "orjson" in sys.modules:
                text = orjson.dumps(data, option=orjson.OPT_INDENT_2).decode("utf-8")
            else:
                text = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            text = data

    elif suffix == ".xml":
        if not isinstance(data, str):
            text = ET.tostring(data, method="xml", xml_declaration=True, encoding="unicode")
        else:
            text = data

    else:
        return Err(f"Type '{suffix}' is not supported")

    # 2. directory check

    dirpath = Path(dirpath)
    if not dirpath.exists():
        if create_dir:
            try:
                os.makedirs(dirpath)
                Trace.update(f"'{dirpath}' created")
            except OSError as err:
                return Err(f"{err}")
        else:
            return Err(f"DirNotFoundError: '{dirpath}'")

    # 3. file check

    filepath = dirpath / filename
    if filepath.exists():
        try:
            with open(filepath, "r", encoding=encoding) as f:
                text_old = f.read()
        except OSError as err:
            return Err(f"{err}")

        if text == text_old:
            Trace.info(f"'{filepath}' not modified")
            return Ok("")

        try:
            with open(filepath, "w", encoding=encoding) as f:
                f.write(text)
        except OSError as err:
            return Err(f"{err}")

        Trace.update(f"'{filepath}' updated")

    else:
        try:
            with open(filepath, "w", encoding=encoding, newline=newline) as f:
                f.write(text)
        except OSError as err:
            return Err(f"{err}")
        Trace.update(f"'{filepath}' created")

    # 4: optional: set file timestamp

    if timestamp > 0:
        try:
            os.utime(filepath, times = (timestamp, timestamp)) # atime and mtime
        except OSError as err:
            return Err(f"timestamp: {err}")

    return Ok(())

def listdir_ext(dirpath: Path | str, extensions: list = None) -> Result[list, str]:
    """
    ---
    list all files in directory which matches the extentions

    Parameters
     - dirpath: Path or str
     - extensions: e.g. str [".zip", ".story", ".xlsx", ".docx"], None => all

    Result [rustedpy]
     - Ok: files as list
     - Err: errortext as str

    """

    dirpath = Path(dirpath)
    if not dirpath.exists():
        return Err(f"DirNotFoundError: '{dirpath}'")

    ret = []
    files = os.listdir(dirpath)
    for file in files:
        if (dirpath / file).is_file():
            if extensions is None or Path(dirpath, file).suffix in extensions:
                ret.append(file)

    return Ok(ret)
