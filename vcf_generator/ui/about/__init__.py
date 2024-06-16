from tkinter import *
import tkinter as tk
from tkinter.ttk import *

from vcf_generator import __version__
from vcf_generator import constants
from vcf_generator.ui.base import BaseWindow
from vcf_generator.util.resource import get_path_in_assets
from vcf_generator.widget.menu import TextContextMenu
from vcf_generator.widget.tkhtmlview import HTMLScrolledText


class AboutWindow(BaseWindow):
    app_icon_image = None

    def on_init_widgets(self):
        self.title(f"关于 {constants.APP_NAME}")
        self.set_size(500, 400)
        self.resizable(False, False)
        header_frame = tk.Frame(self, background="white")
        header_frame.pack(fill=X)
        self.on_init_header(header_frame)
        details_input = HTMLScrolledText(
            self,
            default_font=self.font,
            html=constants.APP_DETAILS,
            state=DISABLED,

        )
        details_input.pack(fill=BOTH, expand=True, **self.scale_values(padx=10, pady=10))
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()

    def on_init_header(self, header_frame: Frame):
        self.app_icon_image = PhotoImage(master=self, file=get_path_in_assets("icon-48.png"))  # 保存到 Window 中防止回收内存
        app_icon_label = tk.Label(header_frame, image=self.app_icon_image, background="white",
                                  **self.scale_values(width=48, height=48))
        app_icon_label.grid(**self.scale_values(row=0, column=0, rowspan=2, **self.scale_values(padx=5, pady=5)))

        app_name_font = self.font.copy()
        app_name_font.config(size=12)
        app_name_label = tk.Label(header_frame, text=constants.APP_NAME, font=app_name_font, background="white")
        app_name_label.grid(row=0, column=1, sticky=SW)
        app_version_label = tk.Label(header_frame, text=f"v{__version__}", background="white")
        app_version_label.grid(row=1, column=1, sticky=NW)


def main():
    window = AboutWindow()
    window.mainloop()


if __name__ == '__main__':
    main()
