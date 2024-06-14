from tkinter import *
from tkinter.ttk import *

from vcf_generator import constants
from vcf_generator.ui.base import BaseWindow


class AboutWindow(BaseWindow):
    def on_init_widgets(self):
        self.title(f"关于 {constants.APP_NAME}")
        self.set_size(400, 600)


def main():
    window = AboutWindow()
    window.mainloop()


if __name__ == '__main__':
    main()
