from tkinter import Misc, Tk
from typing import NamedTuple

from vcf_generator_lite.utils.tkinter.misc import get_root

ATTR_DEFAULT_ACCELERATORS_CACHED = "_default_accelerators_cached"


class DefaultAccelerators(NamedTuple):
    undo: str
    redo: str
    cut: str
    copy: str
    paste: str
    select_all: str


def _create_default_accelerators(root: Tk) -> DefaultAccelerators:
    match root._windowingsystem:  # noqa: SLF001
        case "win32":
            return DefaultAccelerators(
                undo="Ctrl+Z",
                redo="Ctrl+Y",
                cut="Ctrl+X",
                copy="Ctrl+C",
                paste="Ctrl+V",
                select_all="Ctrl+A",
            )
        case "aqua":
            return DefaultAccelerators(
                undo="⌘Z",
                redo="⇧⌘Z",
                cut="⌘X",
                copy="⌘C",
                paste="⌘V",
                select_all="⌘A",
            )
        case _:
            return DefaultAccelerators(
                undo="Ctrl+Z",
                redo="Ctrl+Shift+Z",
                cut="Ctrl+X",
                copy="Ctrl+C",
                paste="Ctrl+V",
                select_all="Ctrl+/",
            )


def get_default_accelerators(master: Misc) -> DefaultAccelerators:
    root = get_root(master)
    if hasattr(root, ATTR_DEFAULT_ACCELERATORS_CACHED):
        return getattr(root, ATTR_DEFAULT_ACCELERATORS_CACHED)

    default_accelerators: DefaultAccelerators = _create_default_accelerators(root)
    setattr(root, ATTR_DEFAULT_ACCELERATORS_CACHED, default_accelerators)
    return default_accelerators
