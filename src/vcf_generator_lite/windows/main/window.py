import webbrowser
from tkinter import Misc
from tkinter.constants import *
from tkinter.ttk import Button, Frame, Label, Progressbar, Sizegrip
from typing import override

from ttk_text.scrolled_text import ScrolledText

from vcf_generator_lite.constants import APP_NAME, URL_LICENSE, URL_RELEASES, URL_REPORT, URL_REPOSITORY
from vcf_generator_lite.layouts.vertical_dialog_layout import VerticalDialogLayout
from vcf_generator_lite.utils.tkinter.menu import MenuBarWindowExtension, MenuCascade, MenuCommand, MenuSeparator
from vcf_generator_lite.utils.tkinter.widget import auto_wrap_configure_event
from vcf_generator_lite.widgets.menu import TextContextMenu
from vcf_generator_lite.windows.base import ExtendedTk
from vcf_generator_lite.windows.base.constants import EVENT_EXIT
from vcf_generator_lite.windows.main.constants import (
    DEFAULT_INPUT_CONTENT,
    EVENT_ABOUT,
    EVENT_CLEAN_QUOTES,
    EVENT_GENERATE,
    USAGE,
)


class MainWindow(ExtendedTk, VerticalDialogLayout, MenuBarWindowExtension):
    generate_button: Button
    content_text: ScrolledText
    progress_bar: Progressbar

    def __init__(self):
        super().__init__(className="VCFGeneratorLite")

    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.title(APP_NAME)
        self.wm_minsize_pt(300, 300)
        self.wm_size_pt(450, 450)
        self._create_widgets(self)
        self._create_menus()

    @override
    def _configure_ui(self):
        super()._configure_ui()
        self.content_text.focus_set()

    @override
    def _create_header(self, parent: Misc):
        description_label = Label(parent, text=USAGE, justify=LEFT)
        description_label.bind("<Configure>", auto_wrap_configure_event, "+")
        description_label.pack(fill=X, padx="7p", pady="7p")
        return description_label

    @override
    def _create_content(self, master: Misc):
        content_frame = Frame(master)
        self.content_text = ScrolledText(content_frame, undo=True, tabs="2c", tabstyle="wordprocessor", maxundo=5)
        self.content_text.insert(0.0, DEFAULT_INPUT_CONTENT)
        self.content_text.edit_reset()
        self.content_text.pack(fill=BOTH, expand=True, padx="7p", pady=0)
        text_context_menu = TextContextMenu(self.content_text)
        text_context_menu.bind_to_widget()
        return content_frame

    @override
    def _create_actions(self, master: Misc):
        action_frame = Frame(master)
        sizegrip = Sizegrip(action_frame)
        sizegrip.place(relx=1, rely=1, anchor=SE)

        self.progress_bar = Progressbar(action_frame, orient=HORIZONTAL, length=200)
        self.progress_label = Label(action_frame, text="正在生成……")

        self.generate_button = Button(
            action_frame, text="开始生成", default=ACTIVE, command=lambda: self.event_generate(EVENT_GENERATE)
        )
        self.generate_button.pack(side=RIGHT, padx="7p", pady="7p")
        return action_frame

    def _create_menus(self):
        self.add_menu_bar_items(
            MenuCascade(
                label="文件(&F)",
                items=[
                    MenuCommand(
                        label="开始生成(&S)…",
                        command=lambda: self.event_generate(EVENT_GENERATE),
                        accelerator="Ctrl + S",
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="退出(&X)",
                        command=lambda: self.event_generate(EVENT_EXIT),
                        accelerator="Alt + F4",
                    ),
                ],
            ),
            MenuCascade(
                label="编辑(&E)",
                items=[
                    MenuCommand(
                        label="撤销(&U)",
                        command=lambda: self.focus_get().event_generate("<<Undo>>"),
                        accelerator="Ctrl + Z",
                    ),
                    MenuCommand(
                        label="重做(&R)",
                        command=lambda: self.focus_get().event_generate("<<Redo>>"),
                        accelerator="Ctrl + Y",
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="剪切(&T)",
                        command=lambda: self.focus_get().event_generate("<<Cut>>"),
                        accelerator="Ctrl + X",
                    ),
                    MenuCommand(
                        label="复制(&C)",
                        command=lambda: self.focus_get().event_generate("<<Copy>>"),
                        accelerator="Ctrl + C",
                    ),
                    MenuCommand(
                        label="粘贴(&P)",
                        command=lambda: self.focus_get().event_generate("<<Paste>>"),
                        accelerator="Ctrl + V",
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="全选(&A)",
                        command=lambda: self.focus_get().event_generate("<<SelectAll>>"),
                        accelerator="Ctrl + A",
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="移除引号(&Q)",
                        command=lambda: self.event_generate(EVENT_CLEAN_QUOTES),
                    ),
                ],
            ),
            MenuCascade(
                label="帮助(&H)",
                items=[
                    MenuCommand(
                        label="源代码仓库(&O)",
                        command=lambda: webbrowser.open(URL_REPOSITORY),
                    ),
                    MenuCommand(
                        label="版本发布网址(&R)",
                        command=lambda: webbrowser.open(URL_RELEASES),
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="提交反馈(&F)…",
                        command=lambda: webbrowser.open(URL_REPORT),
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="许可协议(&L)",
                        command=lambda: webbrowser.open(URL_LICENSE),
                    ),
                    MenuSeparator,
                    MenuCommand(
                        label="关于 VCF 生成器 Lite(&A)",
                        command=lambda: self.event_generate(EVENT_ABOUT),
                    ),
                ],
            ),
        )

    def set_text_content(self, content: str):
        self.content_text.replace(1.0, END, content)

    def get_text_content(self) -> str:
        return self.content_text.get(1.0, END)[:-1]

    def show_progress(self):
        self.progress_bar.pack(side=LEFT, padx="7p", pady="7p")
        self.progress_label.pack(side=LEFT, padx=(0, "7p"), pady="7p")

    def hide_progress(self):
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()

    def set_progress(self, progress: float):
        self.progress_bar.configure(value=progress)

    def set_progress_determinate(self, value: bool):
        previous_value: bool = self.progress_bar.cget("mode") == "determinate"
        if previous_value != previous_value:
            return
        if value:
            self.progress_bar.configure(mode="determinate", maximum=1)
            self.progress_bar.stop()
        else:
            self.progress_bar.configure(mode="indeterminate", maximum=10)
            self.progress_bar.start()

    def set_generate_enabled(self, enabled: bool):
        self.generate_button.configure(state="normal" if enabled else "disabled")
