from tkinter import PhotoImage, Misc, Label as TkLabel
from tkinter.constants import *
from tkinter.ttk import Button, Frame, Label, Style
from typing import override

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT, APP_NAME
from vcf_generator_lite.util.resource import get_about_html, get_asset_scaled_data
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
        self.wm_minsize_pt(375, 300)
        self.wm_maxsize_pt(375, 300)
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
        background_color = Style(master).lookup("InfoHeader.TFrame", "background")
        self.app_icon_image = PhotoImage(
            master=self,
            data=get_asset_scaled_data([
                (1.0, "images/icon-48.png"),
                (1.25, "images/icon-60.png"),
                (1.5, "images/icon-72.png"),

            ], self.scaling() * 0.75),
        )  # 保存到 Window 中防止回收内存
        app_icon_label = TkLabel(
            header_frame,
            image=self.app_icon_image,
            background=background_color,
            width="36p",
            height="36p",
        )
        app_icon_label.pack(side=LEFT, padx="14p", pady="7p")

        app_info_frame = Frame(header_frame, style="InfoHeaderContent.TFrame")
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "14p"), pady="14p")

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
