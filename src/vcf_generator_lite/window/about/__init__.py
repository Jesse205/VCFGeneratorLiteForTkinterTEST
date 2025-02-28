from tkinter import Event, Toplevel, Tk
from typing import Optional

from vcf_generator_lite.window.about.controller import AboutController
from vcf_generator_lite.window.about.window import AboutWindow

about_window: Optional[AboutWindow] = None
about_controller: Optional[AboutController] = None


def _on_destroy(event: Event):
    global about_window, about_controller
    if event.widget is about_window:
        about_window = None
        about_controller = None


def open_about_window(master: Optional[Tk | Toplevel]) -> tuple[AboutWindow, AboutController]:
    global about_window, about_controller
    if about_window is None or not about_window.winfo_exists():
        about_window = AboutWindow(master)
        about_controller = AboutController(about_window)
        about_window.bind("<Destroy>", _on_destroy, "+")
        about_window.bind("<<Generate>>", print, "+")
    about_window.focus()
    return about_window, about_controller
