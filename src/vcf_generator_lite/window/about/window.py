from tkinter import Frame as TkFrame, Label as TkLabel, PhotoImage
from tkinter.constants import *
from tkinter.ttk import Button, Frame, Label, Style
from typing import override

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT, APP_NAME
from vcf_generator_lite.util.resource import get_about_html, get_asset_data
from vcf_generator_lite.util.tkinter.font import extend_font
from vcf_generator_lite.widget.menu import TextContextMenu
from vcf_generator_lite.widget.tkhtmlview import HTMLScrolledText
from vcf_generator_lite.window.base import ExtendedDialog
from vcf_generator_lite.window.base.constants import EVENT_EXIT


class AboutWindow(ExtendedDialog):
    app_icon_image: PhotoImage = None

    @override
    def on_init_window(self):
        super().on_init_window()
        self.title(f"关于 {APP_NAME}")
        self.wm_size_pt(375, 300)
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
        details_input.pack(fill=BOTH, expand=True, padx="8.25p", pady=("8.25p", 0))
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()
        action_frame = Frame(self)
        action_frame.pack(fill=X)
        self.ok_button = Button(
            action_frame,
            text="确定",
            default=ACTIVE,
            command=lambda: self.event_generate(EVENT_EXIT)
        )
        self.ok_button.pack(side=RIGHT, padx="8.25p", pady="8.25p")

    def _create_header(self, master):
        header_frame = Frame(master, style="InfoHeader.TFrame")
        header_background = Style(self).lookup(header_frame.cget("style"), "background")
        self.app_icon_image = PhotoImage(
            master=self,
            data=get_asset_data("images/icon-48.png")
        )  # 保存到 Window 中防止回收内存
        app_icon_label = TkLabel(header_frame, image=self.app_icon_image, background=header_background,
                                 width="36p", height="36p")
        app_icon_label.pack(side=LEFT, padx="8.25p", pady="8.25p")

        app_info_frame = TkFrame(header_frame, background=header_background)
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "8.25p"), pady="8.25p")

        app_name_label = Label(
            app_info_frame,
            text=f"{APP_NAME} v{__version__}",
            background=header_background,
            font=extend_font("TkDefaultFont", size=12)
        )
        app_name_label.pack(anchor=W)
        app_copyright_label = Label(app_info_frame, text=APP_COPYRIGHT, background=header_background)
        app_copyright_label.pack(anchor=W)
        return header_frame
