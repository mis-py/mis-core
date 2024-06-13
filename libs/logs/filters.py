import os
from pathlib import Path


class PathLoguruFilter:
    def __init__(self, path: Path | str, exclude_mode: bool = False):
        self.path = path
        self.exclude_mode = exclude_mode

    def __call__(self, record):
        abs_directory = os.path.abspath(str(self.path))
        is_match = record['file'].path.startswith(abs_directory)

        if is_match and not self.exclude_mode:
            return True
        elif not is_match and self.exclude_mode:
            return True

        return False
