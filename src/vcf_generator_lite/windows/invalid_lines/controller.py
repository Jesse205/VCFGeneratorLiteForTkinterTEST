from collections.abc import Callable
from tkinter import Event

from vcf_generator_lite.core.vcf_generator import InvalidLine
from vcf_generator_lite.models.contact import PhoneNotFoundError
from vcf_generator_lite.windows.invalid_lines.common import st
from vcf_generator_lite.windows.invalid_lines.window import InvalidLinesWindow


def get_locale_exception(exception: BaseException):
    if isinstance(exception, PhoneNotFoundError):
        return st("exception_phone_not_found")
    return str(exception)


class InvalidLinesController:
    def __init__(
        self,
        window: InvalidLinesWindow,
        display_path: str,
        invalid_lines: list[InvalidLine],
    ):
        self.window = window
        self.__line_enter_listener: Callable[[int], None] | None = None
        window.bind("<Return>", self.__on_ok_click)
        window.header_label.configure(text=st("message").format(path=display_path))
        for item in invalid_lines:
            window.content_tree.insert(
                parent="",
                index="end",
                id=item.row_position,
                values=(
                    st("cell_row").format(row=item.row_position),
                    item.content,
                    get_locale_exception(item.exception),
                ),
            )
        window.bind("<Double-Button-1>", self.__on_tree_view_enter)

    def __on_ok_click(self, _: Event):
        self.window.ok_button.invoke()

    def __on_tree_view_enter(self, _: Event):
        selection = self.window.content_tree.selection()
        if self.__line_enter_listener and len(selection) > 0:
            self.__line_enter_listener(int(selection[0]))

    def set_line_enter_listener(self, listener: Callable[[int], None] | None):
        self.__line_enter_listener = listener
