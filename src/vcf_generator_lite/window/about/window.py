from tkinter import PhotoImage, Misc
from tkinter.constants import *
from tkinter.ttk import Button, Frame, Label
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
        details_input.pack(fill=BOTH, expand=True, padx="7p", pady=("7p", 0))
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()
        action_frame = self._create_action_bar(self)
        action_frame.pack(fill=X, side=BOTTOM)

    def _create_header(self, master: Misc):
        header_frame = Frame(master, style="InfoHeader.TFrame")
        self.app_icon_image = PhotoImage(
            master=self,
            data=get_asset_data("images/icon-48.png"),
        )  # 保存到 Window 中防止回收内存
        app_icon_label = Label(
            header_frame,
            image=self.app_icon_image,
            style="InfoHeaderContent.TLabel",
            padding=(self.get_scaled(32.0) - 48.0) / 2,
        )
        app_icon_label.pack(side=LEFT, padx="7p", pady="7p")

        app_info_frame = Frame(header_frame, style="InfoHeaderContent.TFrame")
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "7p"), pady="7p")

        app_name_label = Label(
            app_info_frame,
            text=f"{APP_NAME} v{__version__}",
            style="InfoHeaderContent.TLabel",
            font=extend_font("TkDefaultFont", size=12),
        )
        app_name_label.pack(anchor=W)
        app_copyright_label = Label(app_info_frame, text=APP_COPYRIGHT, style="InfoHeaderContent.TLabel")
        app_copyright_label.pack(anchor=W)
        return header_frame

    def _create_action_bar(self, master: Misc):
        action_frame = Frame(master)
        self.ok_button = Button(
            action_frame,
            text="确定",
            default=ACTIVE,
            command=lambda: self.event_generate(EVENT_EXIT)
        )
        self.ok_button.pack(side=RIGHT, padx="7p", pady="7p")
        return action_frame
