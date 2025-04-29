from tkinter import Label as TkLabel, Misc, PhotoImage
from tkinter.constants import *
from tkinter.ttk import Button, Frame, Label, Style
from typing import override

from vcf_generator_lite import constants, resources
from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT, APP_NAME
from vcf_generator_lite.layout.vertical_dialog_layout import VerticalDialogLayout
from vcf_generator_lite.util.tkinter.font import extend_font
from vcf_generator_lite.widget.menu import TextContextMenu
from vcf_generator_lite.widget.tkhtmlview import HTMLScrolledText
from vcf_generator_lite.window.base import ExtendedDialog
from vcf_generator_lite.window.base.constants import EVENT_EXIT


class AboutWindow(ExtendedDialog, VerticalDialogLayout):
    app_icon_image: PhotoImage

    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.title(f"关于 {APP_NAME}")
        self.wm_size_pt(375, 300)
        self.wm_minsize_pt(375, 300)
        self.wm_maxsize_pt(375, 300)
        self._create_widgets(self)

    @override
    def _create_header(self, parent: Misc):
        header_frame = Frame(parent, style="DialogHeader.TFrame")
        background_color = Style(parent).lookup("DialogHeader.TFrame", "background")
        # 保存到 Window 中防止回收内存
        self.app_icon_image = PhotoImage(
            master=self,
            data=resources.read_scaled_binary(
                resources={
                    1.0: "images/icon-48.png",
                    1.25: "images/icon-60.png",
                    1.5: "images/icon-72.png",
                },
                scaling=round(self.scaling() * 0.75, 2),
            ),
        )
        app_icon_label = TkLabel(
            header_frame,
            image=self.app_icon_image,
            background=background_color,
            width="36p",
            height="36p",
        )
        app_icon_label.pack(side=LEFT, padx="14p", pady="7p")

        app_info_frame = Frame(header_frame, style="DialogHeaderContent.TFrame")
        app_info_frame.pack(side=LEFT, anchor=CENTER, fill=X, expand=True, padx=(0, "14p"), pady="14p")

        app_name_label = Label(
            app_info_frame,
            text=f"{APP_NAME} v{__version__}",
            style="DialogHeaderContent.TLabel",
            font=extend_font("TkDefaultFont", size=12),
        )
        app_name_label.pack(anchor=W)
        app_copyright_label = Label(app_info_frame, text=APP_COPYRIGHT, style="DialogHeaderContent.TLabel")
        app_copyright_label.pack(anchor=W)
        return header_frame

    @override
    def _create_content(self, parent: Misc):
        content_frame = Frame(parent)
        details_input = HTMLScrolledText(
            content_frame,
            html=resources.read_text('texts/about.html').format(
                repository_url=constants.URL_REPOSITORY,
                release_url=constants.URL_RELEASES,
                jesse205_email=constants.EMAIL_JESSE205,
                os_notices_url=constants.URL_OS_NOTICES,
            ),
            state=DISABLED,
        )
        details_input.pack(fill=BOTH, expand=True, padx="7p", pady=("7p", 0))
        details_context_menu = TextContextMenu(details_input)
        details_context_menu.bind_to_widget()
        return content_frame

    @override
    def _create_actions(self, parent: Misc):
        action_frame = Frame(parent)
        self.ok_button = Button(
            action_frame,
            text="确定",
            default=ACTIVE,
            command=lambda: self.event_generate(EVENT_EXIT)
        )
        self.ok_button.pack(side=RIGHT, padx="7p", pady="7p")
        return action_frame
