"""
    © Jürgen Schoenemeyer, 22.02.2025

    src/utils/files.py

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
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple
from xml.dom import minidom

from result import Err, Ok, Result

try:
    import orjson
except ModuleNotFoundError:
    import json

try:
    import xmltodict
except ModuleNotFoundError:
    pass

try:
    from dict2xml import dict2xml  # type: ignore[import-untyped]
except ModuleNotFoundError:
    pass

from utils.trace import Color, Trace

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
        ret = filepath.stat().st_mtime
    except OSError as err:
        Trace.debug(f"{err}")
        return Err(f"{err}")

    return Ok(ret)

def set_timestamp(filepath: Path | str, timestamp: float) -> Result[str, str]:
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

def get_files_dirs(path: Path | str, extensions: List[str]) -> Result[Tuple[List[str], List[str]], str]:
    path = Path(path)

    files: List[str] = []
    dirs: List[str] = []
    try:
        for filename in os.listdir(path):
            filepath = path / filename

            if Path.is_file(filepath):
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

    # 1. file_type check

    suffix  = Path(filename).suffix

    if suffix == ".txt":
        file_type = "text"

    elif suffix == ".json":
        file_type = "json"

    elif suffix == ".xml":
        file_type = "xml"

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
        with Path.open(filepath, mode="r", encoding=encoding) as f:
            text = f.read()
    except OSError as err:
        Trace.debug(f"{err}")
        return Err(f"{err}")

    if file_type == "text":
        return Ok(text)

    elif file_type == "json":
        if "orjson" in sys.modules:
            try:
                data = orjson.loads(text)           # type: ignore[reportPossiblyUnboundVariable]
            except orjson.JSONDecodeError as err:   # type: ignore[reportPossiblyUnboundVariable]
                error = f"JSONDecodeError: {filepath} => {err}"
                Trace.debug(error)
                return Err(error)
            return Ok(data)
        else:
            try:
                data = json.loads(text)             # type: ignore[reportPossiblyUnboundVariable]
            except json.JSONDecodeError as err:     # type: ignore[reportPossiblyUnboundVariable]
                error = f"JSONDecodeError: {filepath} => {err}"
                Trace.debug(error)
                return Err(error)
            return Ok(data)

    elif file_type == "xml":
        try:
            # data = ET.fromstring(text)
            data = minidom.parseString(text)  # noqa: S318
        except (TypeError, AttributeError) as err:
            error = f"ParseError: {err}"
            Trace.debug(error)
            return Err(error)
        return Ok(data)

    else:
        Trace.error(f"Type '{file_type}' is not supported")
        return Err(f"Type '{file_type}' is not supported")


def write_file(filepath: Path | str, data: Any, filename_timestamp: bool = False, timestamp: float = 0, encoding: str="utf-8", newline: str="\n", create_dir: bool = True, show_message: bool=True) -> Result[str, str]:
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
        filename = f"{stem}_{datetime.now().astimezone().strftime(TIMESTAMP)}{suffix}"

    # 1. type check + serialization

    if suffix in [".txt", ".csv"]:
        if not isinstance(data, str):
            err = f'write_file \'{suffix}\': "{str(data)[:50]} …" is not a string'
            Trace.debug(err)
            return Err(err)
        else:
            text = data

    elif suffix == ".json":

        # xml -> json

        if "xmltodict" in sys.modules:
            if isinstance(data, minidom.Document):
                text = data.toxml()
                data = xmltodict.parse(text) # type: ignore[reportPossiblyUnboundVariable]

            elif isinstance(data, ET.Element):
                text = ET.tostring(data, method="xml", xml_declaration=True, encoding="unicode")
                data = xmltodict.parse(text) # type: ignore[reportPossiblyUnboundVariable]
        else:
            err = "module 'xmltodict' not installed"
            Trace.debug(err)
            return Err(err)

        # json -> json

        def serialize_sets(obj: Any) -> Any:
            if isinstance(obj, set):
                return sorted(obj) # type: ignore[reportUnknownVariableType]

            return obj

        if isinstance(data, (dict, list)):
            try:
                if "orjson" in sys.modules:
                    text = orjson.dumps(data, default=serialize_sets, option=orjson.OPT_INDENT_2).decode("utf-8") # type: ignore[reportPossiblyUnboundVariable]
                else:
                    text = json.dumps(data, default=serialize_sets, indent=2, ensure_ascii=False)                 # type: ignore[reportPossiblyUnboundVariable]
            except TypeError as error:
                err = f"TypeError: {error}"
                Trace.error(err)
                return Err(err)
        else:
            err = f"Type '{type(data)}' is not supported for '{suffix}'"
            Trace.error(err)
            return Err(err)

    elif suffix == ".xml":

        # xml -> xml

        if isinstance(data, minidom.Document):
            text = data.toxml()
            text = text.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')

        elif isinstance(data, ET.Element):
            text = ET.tostring(data, method="xml", xml_declaration=True, encoding="unicode")
            text = text.replace("<?xml version='1.0' encoding='utf-8'?>", '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')

        # json -> xml

        elif isinstance(data, (dict, list)):
            if "dict2xml" in sys.modules:
                try:
                    text  = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
                    text += dict2xml(data, wrap="root", indent="  ") # type: ignore[reportPossiblyUnboundVariable]
                except Exception as error:
                    err = f"ValueError: {error}"
                    return Err(err)
            else:
                err = "module 'dict2xml' not installed"
                Trace.debug(err)
                return Err(err)

            # if "dicttoxml" in sys.modules: # GNU License !
            #     try:
            #         xml = dicttoxml(data) # type: ignore[reportPossiblyUnboundVariable]
            #     except ValueError as error:
            #         err = f"ValueError: {error}"
            #         return Err(err)
            #     text = minidom.parseString(xml).toprettyxml(indent="  ")
            #     text = text.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
            # else:
            #     err = "module 'dicttoxml' not installed"
            #     Trace.debug(err)
            #     return Err(err)

        else:
            err = f"Type '{type(data)}' is not supported for '{suffix}'"
            Trace.debug(f"{err}")
            return Err(err)

    else:
        err = f"Type '{suffix}' is not supported"
        Trace.debug(err)
        return Err(err)

    # 2. directory check

    if not dirpath.exists():
        if create_dir:
            try:
                dirpath.mkdir(parents=True)
                Trace.update(f"'{dirpath}' created")
            except OSError as err:
                Trace.debug(f"{err}")
                return Err(f"{err}")
        else:
            return Err(f"DirNotFoundError: '{dirpath}'")

    # 3. file check

    if filepath.exists():
        try:
            with Path.open(filepath, mode="r", encoding=encoding) as f:
                text_old = f.read()
        except OSError as err:
            Trace.debug(f"{err}")
            return Err(f"{err}")

        if text == text_old:
            Trace.info(f"'{filepath}' not modified")
            return Ok("")

        try:
            with Path.open(filepath, mode="w", encoding=encoding, newline=newline) as f:
                f.write(text)
        except OSError as err:
            return Err(f"{err}")

        if show_message:
            Trace.update(f"'{filepath}' updated")

    else:
        try:
            with Path.open(filepath, mode="w", encoding=encoding, newline=newline) as f:
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

    ret: List[str] = []
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

        if path.resolve() == path:
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
                if (success / part).exists() and (success / part).resolve() == (success / part):
                    success = success / part
                else:
                    error = True
                    txt += f"{Color.RED}{Color.BOLD}"

            elif (success / part).exists():
                success = success / part
            else:
                error = True
                txt += f"{Color.RED}{Color.BOLD}"

            txt += part + "/"

    if name == "":
        txt = txt[:-1]
    elif error:
        txt += name
    else:
        txt += f"{Color.RED}{Color.BOLD}{name}"

    txt += f"{Color.RESET}"

    txt = str(Path(txt).as_posix())
    if debug:
        Trace.error( f"path '{txt}' not found" )

    return Err(f"{txt}")
