"""
    © Jürgen Schoenemeyer, 10.01.2025

    error channel -> rustedpy/result

    PUBLIC:
     - result = get_timestamp(filepath: Path | str) -> Result[float, str]
     - result = set_timestamp(filepath: Path | str, timestamp: float) -> Result[(), str]
    #
     - result = get_files_dirs(path: str, extensions: List) -> Result[Tuple[List, List], str]
    #
     - result = read_file(filepath: Path | str, encoding: str="utf-8" ) -> Result[Any, str]
     - result = write_file(filepath: Path | str, data: Any, encoding: str="utf-8", create_dir: bool = True, show_message: bool=True) -> Result[str, str]
    #
    ------
    from result import is_err, is_ok

    if is_err(result):
        Trace.error(f"Error: {result.err_value}")
    else:
        data = result.ok_value

    supported types
     - .txt
     - .json (json or orjson)
     - .xml (minidom or xml.etree.ElementTree)
     #
     ------
     - result = listdir_ext(dirpath: Path | str, extensions: List | None = None) -> Result[List, str]
     - result = check_path_exist(path: Path | str, case_sensitive: bool=False, debug: bool=False) -> Result[str, str]
"""

import os
import sys

from typing import Any, Dict, List, Tuple
from datetime import datetime
from pathlib import Path

from xml.dom import minidom
import xml.etree.ElementTree as ET

try:
    import xmltodict
except ModuleNotFoundError:
    pass

try:
    import dicttoxml # type: ignore # -> mypy
except ModuleNotFoundError:
    pass

try:
    import orjson
except ModuleNotFoundError:
    import json

from result import Result, Ok, Err

from utils.trace import Trace, Color

TIMESTAMP = "%Y-%m-%d_%H-%M-%S"

def get_timestamp(filepath: Path | str) -> Result[float, str]:
    """
    ### get timestamp of a file

    #### Arguments
     - filepath: Path or str

    #### Return [rustedpy]
     - Ok: timestamp as float
     - Err: errortext as str
    """

    filepath = Path(filepath)

    if not filepath.exists():
        err = f"'{filepath}' does not exist"
        Trace.debug(err)
        return Err(err)

    try:
        ret = os.path.getmtime(Path(filepath))
    except OSError as err:
        Trace.debug(f"{err}")
        return Err(f"{err}")

    return Ok(ret)

def set_timestamp(filepath: Path | str, timestamp: int|float) -> Result[str, str]:
    """
    ### set timestamp of a file

    #### Arguments
     - filepath: Path or str
     - timestamp: float

    #### Return [rustedpy]
     - Ok: -
     - Err: errortext as str
    """

    filepath = Path(filepath)

    if not filepath.exists():
        err = f"'{filepath}' does not exist"
        Trace.debug(f"{err}")
        return Err(err)

    try:
        os.utime(Path(filepath), times = (timestamp, timestamp)) # atime and mtime
    except OSError as err:
        Trace.debug(f"{err}")
        return Err(f"{err}")

    return Ok("")

# dir listing -> list of files and dirs

def get_files_dirs(path: str, extensions: List[str]) -> Result[Tuple[List[str], List[str]], str]:
    files: List[str] = []
    dirs: List[str] = []
    try:
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)

            if os.path.isfile(filepath):
                for extention in extensions:
                    if "." + extention in filename:
                        files.append(filename)
                        break
            else:
                dirs.append(filename)

    except OSError as err:
        Trace.error(f"{err}")
        return Err(f"{err}")

    return Ok((files, dirs))

def read_file(filepath: Path | str, encoding: str="utf-8") -> Result[Any, str]:
    """
    ### read file (text, json, xml)

    #### Arguments
     - filepath: Path or str  - supported suffixes: '.txt', '.json', '.xml'
     - encoding: str - used only for '.txt'

    #### Return [rustedpy]
     - Ok: data as Any
     - Err: errortext as str
    ---
    #### Infos
     - using orjson (if installed) for '.json' files
     - auto convert (xml <-> json)
     - xml used minidom or xml.etree.ElementTree
    """

    filepath = Path(filepath)
    dirpath  = Path(filepath).parent
    filename = Path(filepath).name

    # 1. type check

    suffix  = Path(filename).suffix

    if suffix == ".txt":
        type = "text"

    elif suffix == ".json":
        type = "json"

    elif suffix == ".xml":
        type = "xml"

    else:
        err = f"Type '{suffix}' is not supported"
        Trace.debug(err)
        return Err(err)

    # 2. directory check

    if not dirpath.exists():
        err = f"DirNotFoundError: '{dirpath}'"
        Trace.debug(err)
        return Err(err)

    # 3. file check + deserialization

    if not filepath.exists():
        err = f"FileNotFoundError: '{filepath}'"
        Trace.debug(err)
        return Err(err)

    try:
        with open(filepath, "r", encoding=encoding) as f:
            text = f.read()
    except OSError as err:
        Trace.debug(f"{err}")
        return Err(f"{err}")

    if type == "text":
        return Ok(text)

    elif type == "json":
        if "orjson" in sys.modules:
            try:
                data = orjson.loads(text)
            except orjson.JSONDecodeError as err:
                error = f"JSONDecodeError: {filepath} => {err}"
                Trace.debug(error)
                return Err(error)
            return Ok(data)
        else:
            try:
                data = json.loads(text)
            except json.JSONDecodeError as err:
                error = f"JSONDecodeError: {filepath} => {err}"
                Trace.debug(error)
                return Err(error)
            return Ok(data)

    elif type == "xml":
        try:
            # data = ET.fromstring(text)
            data = minidom.parseString(text)
        except (TypeError, AttributeError) as err:
            error = f"ParseError: {err}"
            Trace.debug(error)
            return Err(error)
        return Ok(data)

    else:
        Trace.error(f"Type '{type}' is not supported")
        return Err(f"Type '{type}' is not supported")


def write_file(filepath: Path | str, data: Any, filename_timestamp: bool = False, timestamp: int|float = 0, encoding: str="utf-8", newline: str="\n", create_dir: bool = True, show_message: bool=True) -> Result[str, str]:
    """
    ### write file (text, json, xml)

    #### Arguments
     - filepath: Path or str - supported suffixes: '.txt', '.json', '.xml'
     - filename_timestamp: bool - add timestamp to filename
     - timestamp: float - timestamp in sec
     - encoding: str - used only for '.txt'
     - newline: str - "\\n" or "\\r\\n"
     - create_dir: bool - create directory if not exists (default: True)

    #### Returns [rustedpy]
     - Ok: -
     - Err: errortext as str
    ----
    #### Infos
     - using orjson (if installed) for '.json' files
     - auto convert (xml <-> json)
     - xml used minidom or xml.etree.ElementTree
    """

    filepath = Path(filepath)
    dirpath  = Path(filepath).parent
    filename = Path(filepath).name

    suffix = Path(filename).suffix
    stem = Path(filename).stem

    if filename_timestamp:
        filename = f"{stem}_{datetime.now().strftime(TIMESTAMP)}{suffix}"

    # 1. type check + serialization

    if suffix in [".txt", ".csv"]:
        if not isinstance(data, str):
            err = f'write_file \'{suffix}\': "{str(data)[:50]} …" is not a string'
            Trace.debug(err)
            return Err(err)
        else:
            text = data

    elif suffix == ".json":

        # xxl -> json

        if isinstance(data, minidom.Document):
            text = data.toxml()
            data = xmltodict.parse(text)

        elif isinstance(data, ET.Element):
            text = ET.tostring(data, method="xml", xml_declaration=True, encoding="unicode")
            data = xmltodict.parse(text)

        # json -> json

        def serialize_sets(obj: Any) -> Any:
            if isinstance(obj, set):
                return sorted(obj)

            return obj

        if isinstance(data, Dict) or isinstance(data, List):
            try:
                if "orjson" in sys.modules:
                    text = orjson.dumps(data, default=serialize_sets, option=orjson.OPT_INDENT_2).decode("utf-8")
                else:
                    text = json.dumps(data, default=serialize_sets, indent=2, ensure_ascii=False)
            except TypeError as err:
                error = f"TypeError: {err}"
                Trace.error(error)
                return Err(error)
        else:
            error = f"Type '{type(data)}' is not supported for '{suffix}'"
            Trace.error(error)
            return Err(error)

    elif suffix == ".xml":

        # xml -> xml

        if isinstance(data, minidom.Document):
            text = data.toxml()
            text = text.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')

        elif isinstance(data, ET.Element):
            text = ET.tostring(data, method="xml", xml_declaration=True, encoding="unicode")
            text = text.replace("<?xml version='1.0' encoding='utf-8'?>", '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')

        # json -> xml

        elif isinstance(data, Dict):
            text = minidom.parseString(dicttoxml(data)).toprettyxml(indent="  ")
            text = text.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')

        else:
            error = f"Type '{type(data)}' is not supported for '{suffix}'"
            Trace.debug(f"{error}")
            return Err(error)

    else:
        error = f"Type '{suffix}' is not supported"
        Trace.debug(error)
        return Err(error)

    # 2. directory check

    if not dirpath.exists():
        if create_dir:
            try:
                os.makedirs(dirpath)
                Trace.update(f"'{dirpath}' created")
            except OSError as err:
                Trace.debug(f"{err}")
                return Err(f"{err}")
        else:
            return Err(f"DirNotFoundError: '{dirpath}'")

    # 3. file check

    if filepath.exists():
        try:
            with open(filepath, "r", encoding=encoding) as f:
                text_old = f.read()
        except OSError as err:
            Trace.debug(f"{err}")
            return Err(f"{err}")

        if text == text_old:
            Trace.info(f"'{filepath}' not modified")
            return Ok("")

        try:
            with open(filepath, "w", encoding=encoding) as f:
                f.write(text)
        except OSError as err:
            return Err(f"{err}")

        if show_message:
            Trace.update(f"'{filepath}' updated")

    else:
        try:
            with open(filepath, "w", encoding=encoding, newline=newline) as f:
                f.write(text)
        except OSError as err:
            Trace.debug(f"{err}")
            return Err(f"{err}")

        if show_message:
            Trace.update(f"'{filepath}' created")

    # 4: optional: set file timestamp

    if timestamp > 0:
        try:
            os.utime(filepath, times = (timestamp, timestamp)) # atime and mtime
        except OSError as err:
            Trace.debug(f"{err}")
            return Err(f"timestamp: {err}")

    return Ok("")

def listdir_ext(dirpath: Path | str, extensions: List[str] | None = None) -> Result[List[str], str]:
    """
    ### List all files in directory which matches the extentions

    #### Arguments
     - dirpath: Path or str
     - extensions: e.g. str [".zip", ".story", ".xlsx", ".docx"], None => all

    #### Return [rustedpy]
     - Ok: files as List
     - Err: errortext as str
    """

    dirpath = Path(dirpath)
    if not dirpath.exists():
        err = f"DirNotFoundError: '{dirpath}'"
        Trace.debug(err)
        return Err(err)

    ret = []
    files = os.listdir(dirpath)
    for file in files:
        if (dirpath / file).is_file():
            if extensions is None or Path(dirpath, file).suffix in extensions:
                ret.append(file)

    return Ok(ret)

def check_path_exist(path: Path | str, case_sensitive: bool=False, debug: bool=False) -> Result[str, str]:
    if str(path)[-1] == ":":
        path = str(path) + "/"

    path = Path(path)

    if path.exists():
        if not case_sensitive:
            return Ok(f"{Color.GREEN}{path.as_posix()}{Color.RESET}")

        if os.path.abspath(path) == os.path.realpath(path):
            return Ok(f"{Color.GREEN}{path.as_posix()}{Color.RESET}")

    name = ""
    suffix = path.suffix

    if suffix != "":
        name = path.name
        path = path.parent

    error = False
    success = Path()

    txt = f"{Color.GREEN}"
    for part in path.parts:
        if not error:
            if case_sensitive:
                if (success / part).exists() and os.path.abspath(success / part) == os.path.realpath(success / part):
                    success = success / part
                else:
                    error = True
                    txt += f"{Color.RED}{Color.BOLD}"

            else:
                if (success / part).exists():
                    success = success / part
                else:
                    error = True
                    txt += f"{Color.RED}{Color.BOLD}"

        txt += part + "/"

    if name == "":
        txt = txt[:-1]
    else:
        if error:
            txt += name
        else:
            txt += f"{Color.RED}{Color.BOLD}{name}"

    txt += f"{Color.RESET}"

    txt = str(Path(txt).as_posix())
    if debug:
        Trace.error( f"path '{txt}' not found" )

    return Err(f"{txt}")