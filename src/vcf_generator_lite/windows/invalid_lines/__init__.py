from tkinter import Tk, Toplevel

from vcf_generator_lite.services.vcf_generator import InvalidLine
from vcf_generator_lite.windows.invalid_lines.controller import InvalidLinesController
from vcf_generator_lite.windows.invalid_lines.window import InvalidLinesWindow


def create_invalid_lines_window(
    master: Tk | Toplevel, display_path: str, invalid_lines: list[InvalidLine]
) -> tuple[InvalidLinesWindow, InvalidLinesController]:
    invalid_lines_window = InvalidLinesWindow(master)
    invalid_lines_controller = InvalidLinesController(invalid_lines_window, display_path, invalid_lines)
    return invalid_lines_window, invalid_lines_controller
