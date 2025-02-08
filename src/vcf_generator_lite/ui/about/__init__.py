import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from typing import Optional

from vcf_generator_lite import __version__
from vcf_generator_lite import constants
from vcf_generator_lite.ui.base import BaseDialog
from vcf_generator_lite.util.resource import get_about_html, get_asset_data
from vcf_generator_lite.util.style.font import extend_font
from vcf_generator_lite.widget.menu import TextContextMenu
from vcf_generator_lite.widget.tkhtmlview import HTMLScrolledText

EVENT_ON_OK_CLICK = "<<OnOkClick>>"


class AboutWindow(BaseDialog):
    app_icon_image = None

    def on_init_window(self):
        super().on_init_window()
        self.title(f"关于 {constants.APP_NAME}")
        self.set_size(500, 400)
        self._create_widgets()

    def _create_widgets(self):
        header_frame = self._create_header(self)
        header_frame.pack(fill=X)
        details_input = HTMLScrolledText(
            self,
            html=get_about_html(),
            state=DISABLED,
            height=0,
        )
        details_input.pack(fill=BOTH, expand=True, padx="10p", pady=("10p", 0))
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()
        action_frame = Frame(self)
        action_frame.pack(fill=X)
        ok_button = Button(action_frame, text="确定", default=ACTIVE,
                           command=lambda: self.event_generate(EVENT_ON_OK_CLICK))
        ok_button.pack(side=RIGHT, padx="10p", pady="10p")

    def _create_header(self, master):
        header_frame = Frame(master, style="InfoHeader.TFrame")
        header_background = Style(self).lookup(header_frame.cget("style"), "background")
        self.app_icon_image = PhotoImage(
            master=self,
            data=get_asset_data("images/icon-48.png")
        )  # 保存到 Window 中防止回收内存
        app_icon_label = tk.Label(header_frame, image=self.app_icon_image, background=header_background,
                                  width="48p", height="48p")
        app_icon_label.pack(side=LEFT, padx="10p", pady="10p")

        app_info_frame = tk.Frame(header_frame, background=header_background)
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "10p"), pady="10p")

        app_name_label = tk.Label(
            app_info_frame,
            text=f"{constants.APP_NAME} v{__version__}",
            background=header_background
        )
        app_name_label.configure(font=extend_font(app_name_label.cget("font"), size=16))
        app_name_label.pack(anchor=W)
        app_copyright_label = tk.Label(app_info_frame, text=constants.APP_COPYRIGHT, background=header_background)
        app_copyright_label.pack(anchor=W)
        return header_frame


class AboutController:
    def __init__(self, window: AboutWindow):
        self.window = window
        window.bind(EVENT_ON_OK_CLICK, self.on_ok_click)
        window.bind("<Return>", self.on_ok_click)
        window.bind("<Escape>", self.on_escape_click)

    def on_ok_click(self, _: Event):
        self.window.destroy()

    def on_escape_click(self, _: Event):
        self.window.destroy()


about_window: Optional[AboutWindow] = None
about_controller: Optional[AboutController] = None


def _on_destroy(event: Event):
    global about_window, about_controller
    if event.widget is about_window:
        about_window = None
        about_controller = None


def open_about_window(master: Optional[Misc]) -> tuple[AboutWindow, AboutController]:
    global about_window, about_controller
    if about_window is None or not about_window.winfo_exists():
        about_window = AboutWindow(master)
        about_controller = AboutController(about_window)
        about_window.bind("<Destroy>", _on_destroy, "+")
    about_window.focus()
    return about_window, about_controller
