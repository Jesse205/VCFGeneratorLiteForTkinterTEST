from tkinter import Misc

# Edit accelerators
ACCELERATOR_UNDO = "Ctrl+Z"
ACCELERATOR_REDO_WINDOWS = "Ctrl+Y"
ACCELERATOR_REDO_X11 = "Ctrl+Shft+Z"
ACCELERATOR_CUT = "Ctrl+X"
ACCELERATOR_COPY = "Ctrl+C"
ACCELERATOR_PASTE = "Ctrl+V"
ACCELERATOR_SELECT_ALL = "Ctrl+A"
# ACCELERATOR_CLOSE = "Alt+F4"


def get_accelerator_redo(master: Misc) -> str:
    match master._windowingsystem:
        case "win32":
            return ACCELERATOR_REDO_WINDOWS
        case _:
            return ACCELERATOR_REDO_X11
