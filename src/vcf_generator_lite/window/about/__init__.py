from tkinter import Event, Tk, Toplevel
from typing import Optional

from vcf_generator_lite.window.about.controller import AboutController
from vcf_generator_lite.window.about.window import AboutWindow


class AboutOpener:

    def __init__(self, master: Tk | Toplevel):
        self.master = master
        self.window: Optional[AboutWindow] = None
        self.controller: Optional[AboutController] = None

    def open(self):
        if self.window is None or not self.window.winfo_exists():
            self.window = AboutWindow(self.master)
            self.window.bind("<Destroy>", self._on_about_destroy, "+")
            self.controller = AboutController(self.window)
        self.window.focus()

    def _on_about_destroy(self, event: Event):
        if event.widget is self.window:
            self.window = None
            self.controller = None
