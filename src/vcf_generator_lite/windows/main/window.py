import urllib.parse
from tkinter import Menu, Misc, Text
from tkinter.ttk import Button, Frame, Label, Progressbar, Sizegrip
from typing import Literal, override

from ttk_text.scrolled_text import ScrolledText

from vcf_generator_lite.constants import (
    EMAIL_JESSE205,
    URL_LICENSE,
    URL_OS_NOTICES,
    URL_RELEASES,
    URL_REPORT,
    URL_REPOSITORY,
)
from vcf_generator_lite.layouts.vertical_dialog_layout import VerticalDialogLayout
from vcf_generator_lite.utils.external_app import open_url_with_fallback
from vcf_generator_lite.utils.locales import scope, t
from vcf_generator_lite.utils.tkinter.accelerators import get_default_accelerators
from vcf_generator_lite.utils.tkinter.busy import tk_busy_forget, tk_busy_hold, tk_busy_status
from vcf_generator_lite.utils.tkinter.menu import parse_menu_label
from vcf_generator_lite.utils.tkinter.widget import enable_auto_wrap
from vcf_generator_lite.widgets.line_number_bar import LineNumberBar
from vcf_generator_lite.widgets.text_menu import TextContextMenu
from vcf_generator_lite.windows.base import EnhancedTk
from vcf_generator_lite.windows.base.constants import EVENT_EXIT
from vcf_generator_lite.windows.main.constants import (
    ACCELERATOR_GENERATE,
    ACCELERATOR_GENERATE_AQUA,
    EVENT_ABOUT,
    EVENT_CLEAN_QUOTES,
    EVENT_GENERATE,
    EVENT_GENERATE_OR_STOP,
    EVENT_STOP,
)

st = scope("main_window")


class VCFGeneratorLiteApp(EnhancedTk, VerticalDialogLayout):
    generate_or_stop_button: Button
    content_text: ScrolledText
    progress_bar: Progressbar

    def __init__(self):
        super().__init__(className="VCFGeneratorLite")

    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.title(t("app_name"))
        self.wm_minsize_pt(300, 300)
        self.wm_size_pt(450, 450)
        self._create_widgets(self)
        menu_bar = self._create_menu_bar()
        self.configure(menu=menu_bar)

    @override
    def _configure_ui(self):
        super()._configure_ui()
        self.content_text.focus_set()

    @override
    def _create_header(self, parent: Misc):
        description_label = Label(parent, text=st("usage"), justify="left")
        enable_auto_wrap(description_label)
        description_label.pack(fill="x", padx="7p", pady="7p")
        return description_label

    @override
    def _create_content(self, parent: Misc):
        self.content_text = ScrolledText(parent, undo=True, tabs="2c", tabstyle="wordprocessor", maxundo=5)
        self.content_text.insert(0.0, st("input_example"))
        self.content_text.edit_reset()
        self.content_text.pack(fill="both", expand=True, padx="7p", pady=0)

        self.line_numbers = LineNumberBar(self.content_text.frame)
        self.line_numbers.bind_text(self.content_text)
        self.line_numbers.grid(row=1, column=0, sticky="ns")
        self.__update_line_numbers_padding()
        self.content_text.frame.bind_widget(self.line_numbers, penetration_state=True)
        self.content_text.bind("<<ThemeChanged>>", lambda _: self.__update_line_numbers_padding(), "+")

        text_context_menu = TextContextMenu(self.content_text)
        text_context_menu.bind_to_widget()
        return self.content_text

    def __update_line_numbers_padding(self):
        self.line_numbers.grid(pady=Text.grid_info(self.content_text).get("pady", None))

    @override
    def _create_footer(self, parent: Misc):
        footer_frame = Frame(parent)
        sizegrip = Sizegrip(footer_frame)
        sizegrip.place(relx=1, rely=1, anchor="se")

        self.progress_bar = Progressbar(footer_frame, orient="horizontal", length=200)
        self.progress_label = Label(master=footer_frame, text=st("label_generating"))

        self.generate_or_stop_button = Button(
            footer_frame,
            text=st("button_generate"),
            default="active",
            command=lambda: self.event_generate(EVENT_GENERATE_OR_STOP),
        )
        self.generate_or_stop_button.pack(side="right", padx="7p", pady="7p")
        return footer_frame

    def _create_menu_bar(self):
        menu_bar = Menu(self, tearoff=False, name="menubar")
        menu_bar.add_cascade(
            **parse_menu_label(st("menu_file")),
            menu=self._create_file_menu(menu_bar),
        )
        menu_bar.add_cascade(
            **parse_menu_label(st("menu_edit")),
            menu=self._create_edit_menu(menu_bar),
        )
        menu_bar.add_cascade(
            **parse_menu_label(st("menu_help")),
            menu=self._create_help_menu(menu_bar),
        )
        return menu_bar

    def _create_file_menu(self, master: Misc):
        self.file_menu = file_menu = Menu(master, tearoff=False)

        generate_parse_result = parse_menu_label(st("menu_file_generate"))
        self.menu_generate_label = generate_parse_result["label"]
        file_menu.add_command(
            **generate_parse_result,
            command=lambda: self.event_generate(EVENT_GENERATE),
            accelerator=ACCELERATOR_GENERATE_AQUA if self._windowingsystem == "aqua" else ACCELERATOR_GENERATE,
        )

        stop_generation_parse_result = parse_menu_label(st("menu_file_stop_generation"))
        self.menu_stop_generation_label = stop_generation_parse_result["label"]
        file_menu.add_command(
            **stop_generation_parse_result,
            command=lambda: self.event_generate(EVENT_STOP),
            accelerator=ACCELERATOR_GENERATE_AQUA if self._windowingsystem == "aqua" else ACCELERATOR_GENERATE,
            state="disabled",
        )

        file_menu.add_separator()
        # 通常不提供退出的快捷键
        # https://learn.microsoft.com/en-us/windows/win32/uxguide/cmd-menus
        file_menu.add_command(
            **parse_menu_label(st("menu_file_exit")),
            command=lambda: self.event_generate(EVENT_EXIT),
        )
        return file_menu

    def _create_edit_menu(self, master: Misc):
        default_accelerators = get_default_accelerators(self)

        edit_menu = Menu(master, tearoff=False)
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_undo")),
            command=lambda: self.__generate_focus_event("<<Undo>>"),
            accelerator=default_accelerators.undo,
        )
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_redo")),
            command=lambda: self.__generate_focus_event("<<Redo>>"),
            accelerator=default_accelerators.redo,
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_cut")),
            command=lambda: self.__generate_focus_event("<<Cut>>"),
            accelerator=default_accelerators.cut,
        )
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_copy")),
            command=lambda: self.__generate_focus_event("<<Copy>>"),
            accelerator=default_accelerators.copy,
        )
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_paste")),
            command=lambda: self.__generate_focus_event("<<Paste>>"),
            accelerator=default_accelerators.paste,
        )
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_select_all")),
            command=lambda: self.__generate_focus_event("<<SelectAll>>"),
            accelerator=default_accelerators.select_all,
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            **parse_menu_label(st("menu_edit_clean_quotes")),
            command=lambda: self.event_generate(EVENT_CLEAN_QUOTES),
        )
        return edit_menu

    def _create_help_menu(self, master: Misc):
        help_menu = Menu(master, tearoff=False, name="help")
        help_menu.add_command(
            **parse_menu_label(st("menu_help_repository")),
            command=lambda: open_url_with_fallback(self, URL_REPOSITORY),
        )
        help_menu.add_command(
            **parse_menu_label(st("menu_help_release")),
            command=lambda: open_url_with_fallback(self, URL_RELEASES),
        )
        help_menu.add_separator()
        help_menu.add_command(
            **parse_menu_label(st("menu_help_feedback")),
            command=lambda: open_url_with_fallback(self, URL_REPORT),
        )
        help_menu.add_command(
            **parse_menu_label(st("menu_help_contact")),
            command=lambda: open_url_with_fallback(
                parent=self,
                url=urllib.parse.SplitResult(
                    scheme="mailto",
                    netloc="",
                    path=EMAIL_JESSE205,
                    query="",
                    fragment="",
                ).geturl(),
            ),
        )
        help_menu.add_separator()
        help_menu.add_command(
            **parse_menu_label(st("menu_help_license")),
            command=lambda: open_url_with_fallback(self, URL_LICENSE),
        )
        help_menu.add_command(
            **parse_menu_label(st("menu_help_os_notices")),
            command=lambda: open_url_with_fallback(self, URL_OS_NOTICES),
        )
        help_menu.add_separator()
        help_menu.add_command(
            **parse_menu_label(st("menu_help_about")),
            command=lambda: self.event_generate(EVENT_ABOUT),
        )
        return help_menu

    def __generate_focus_event(self, sequence: str):
        if widget := self.focus_get():
            widget.event_generate(sequence)

    def set_text_content(self, content: str):
        self.content_text.replace(1.0, "end", content)

    def get_text_content(self) -> str:
        return self.content_text.get(1.0, "end")[:-1]

    def show_progress(self):
        self.progress_bar.pack(side="left", padx="7p", pady="7p")
        self.progress_label.pack(side="left", padx=(0, "7p"), pady="7p")

    def hide_progress(self):
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()

    def set_progress(self, progress: float):
        self.progress_bar.configure(value=progress)

    def set_progress_determinate(self, value: bool):
        previous_value: bool = self.progress_bar.cget("mode") == "determinate"
        if value == previous_value:
            return
        if value:
            self.progress_bar.configure(mode="determinate", maximum=1)
            self.progress_bar.stop()
        else:
            self.progress_bar.configure(mode="indeterminate", maximum=10)
            self.progress_bar.start()

    def set_generating(self, state: bool | Literal["stopping"]):
        if state is True:
            self.generate_or_stop_button.configure(text=st("button_stop"), state="normal")
            if tk_busy_status(self.generate_or_stop_button):
                tk_busy_forget(self.generate_or_stop_button)
            self.progress_label.configure(text=st("label_generating"))
            self.show_progress()
        elif state is False:
            self.generate_or_stop_button.configure(text=st("button_generate"), state="normal")
            if tk_busy_status(self.generate_or_stop_button):
                tk_busy_forget(self.generate_or_stop_button)
            self.hide_progress()
        elif state == "stopping":
            self.generate_or_stop_button.configure(text=st("button_stop"), state="disabled")
            if not tk_busy_status(self.generate_or_stop_button):
                tk_busy_hold(self.generate_or_stop_button)
            self.progress_label.configure(text=st("label_stopping"))
            self.show_progress()
            self.set_progress_determinate(False)
        self.file_menu.entryconfigure(self.menu_generate_label, state="normal" if state is False else "disabled")
        self.file_menu.entryconfigure(self.menu_stop_generation_label, state="normal" if state is True else "disabled")
