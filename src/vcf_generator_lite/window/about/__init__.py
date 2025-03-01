from tkinter import Event, Toplevel, Tk
from typing import Optional

from vcf_generator_lite.window.about.controller import AboutController
from vcf_generator_lite.window.about.window import AboutWindow


class AboutOpener:
    window: Optional[AboutWindow] = None
    controller: Optional[AboutController] = None

    def __init__(self, master: Tk | Toplevel):
        self.master = master

    def open(self):
        if self.window is None or not self.window.winfo_exists():
            self.window = AboutWindow(self.master)
            AboutController(self.window)
        self.window.focus()

    def _on_about_destroy(self, event: Event):
        if event.widget is self.window:
            self.window = None
            self.about_controller = None
