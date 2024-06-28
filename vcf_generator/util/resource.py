import os
import sys
from typing import Optional

print()


def get_path_in_assets(file_name: str) -> str:
    """
    Get the path to the file in the assets' folder.
    :param file_name: The name of the file.
    :return: The path to the file.
    """
    return os.path.join(os.path.dirname(sys.modules["vcf_generator"].__file__), "assets", file_name)


def get_window_icon() -> Optional[str]:
    if sys.platform == "win32":
        return get_path_in_assets("images/icon.ico")
    return None


def get_default_color() -> str:
    if sys.platform == "win32":
        return "SystemHighlight"
    return "blue"
