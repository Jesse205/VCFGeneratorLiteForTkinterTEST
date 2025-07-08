from tkinter import Event

from vcf_generator_lite.windows.about.window import AboutWindow


class AboutController:
    def __init__(self, window: AboutWindow):
        self.window = window
        window.bind("<Return>", self.on_ok_click)

    def on_ok_click(self, _: Event):
        self.window.ok_button.invoke()
