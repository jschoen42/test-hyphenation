# python __mypy.py src/main.py
# uv run __mypy.py src/main.py

import sys
import subprocess
import platform

from typing import List
from pathlib import Path
from datetime import datetime

BASE_PATH = Path(sys.argv[0]).parent.parent.resolve()

def run_mypy() -> None:

    # https://mypy.readthedocs.io/en/stable/command_line.html

    settings: List[str] = [
        # Incremental mode
        "--sqlite-cache",

        # Untyped definitions and calls
        "--disallow-untyped-calls",
        "--disallow-untyped-defs",
        "--disallow-untyped-decorators",
        "--disallow-incomplete-defs",

        # Configuring warnings
        "--warn-redundant-casts",
        "--warn-unused-ignores",
        "--warn-unreachable",

        # Miscellaneous strictness flags
        "--strict-equality",

        # Configuring error messages
        # "--show-error-context"
        "--show-column-numbers",
        # "--show-error-end",
        # "--show-error-code-links".
        # "--pretty",
        # "--force-uppercase-builtins",

        # Advanced options
        # "--show-traceback",
        # "--strict",
    ]

    filepath = Path(sys.argv[1]).stem

    text =  f"Python:   {sys.version}\n"
    text += f"Platform: {platform.platform()}\n"
    text += f"Date:     {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n"
    text += f"Path:     {BASE_PATH}\n"
    text += "\n"

    text += "MyPy settings:\n"
    for setting in settings:
        text += f" {setting}\n"

    text += "\n"

    result = subprocess.run(["mypy"] + (settings + sys.argv[1:]), capture_output=True, text=True)

    current_file = None
    for line in result.stdout.splitlines():
        if line and not line.startswith(" "):
            file_path = line.split(":")[0]
            if file_path != current_file:
                if current_file is not None:
                    text += "\n"
                current_file = file_path

        text += f"{line}\n"

    with open(f"__mypy-{filepath}.txt", "w") as file:
        file.write(text)

    sys.exit(result.returncode)

if __name__ == "__main__":
    run_mypy()
