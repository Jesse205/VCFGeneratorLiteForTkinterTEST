import tkinter as tk
from tkinter import *
from tkinter.ttk import *

from vcf_generator import __version__
from vcf_generator import constants
from vcf_generator.ui.base import BaseDialog
from vcf_generator.util.resource import get_about_html, get_asset_data
from vcf_generator.widget.menu import TextContextMenu
from vcf_generator.widget.tkhtmlview import HTMLScrolledText


class AboutWindow(BaseDialog):
    app_icon_image = None

    def on_init_window(self):
        super().on_init_window()
        self.title(f"关于 {constants.APP_NAME}")
        self.set_size(500, 400)
        self.resizable(False, False)

    def on_init_widgets(self):
        header_frame = tk.Frame(self, background="systemWindow")
        header_frame.pack(fill=X)
        self.on_init_header(header_frame)
        details_input = HTMLScrolledText(
            self,
            default_font=self.font,
            html=get_about_html(),
            state=DISABLED,
        )
        details_input.pack(fill=BOTH, expand=True, padx="10p", pady="10p")
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()

    def on_init_header(self, header_frame: Frame):
        header_background = header_frame.cget("background")
        self.app_icon_image = PhotoImage(master=self,
                                         data=get_asset_data("images/icon-48.png"))  # 保存到 Window 中防止回收内存
        app_icon_label = tk.Label(header_frame, image=self.app_icon_image, background=header_background,
                                  width="48p", height="48p")
        app_icon_label.pack(side=LEFT, padx="10p", pady="10p")

        app_info_frame = tk.Frame(header_frame, background=header_background)
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "10p"), pady="10p")

        app_name_font = self.font.copy()
        app_name_font.config(size=16)
        app_name_label = tk.Label(
            app_info_frame,
            text=f"{constants.APP_NAME} v{__version__}",
            font=app_name_font,
            background=header_background
        )
        app_name_label.pack(anchor=W)
        app_copyright_label = tk.Label(app_info_frame, text=constants.APP_COPYRIGHT, background=header_background)
        app_copyright_label.pack(anchor=W)


_about_window_instance: AboutWindow | None = None


def _on_destroy(event: Event):
    global _about_window_instance
    if event.widget is _about_window_instance:
        _about_window_instance = None


def open_about_window(master: Misc | None = None) -> tuple[AboutWindow]:
    global _about_window_instance
    if _about_window_instance is None or not _about_window_instance.winfo_exists():
        _about_window_instance = AboutWindow(master)
        _about_window_instance.bind("<Destroy>", _on_destroy, "+")
    _about_window_instance.focus()
    return _about_window_instance,
