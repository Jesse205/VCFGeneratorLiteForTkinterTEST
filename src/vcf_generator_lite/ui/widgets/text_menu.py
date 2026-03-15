from tkinter import Entry, Menu, TclError, Text
from tkinter.constants import SEL_FIRST
from typing import Literal

from vcf_generator_lite.utils.locales import scope
from vcf_generator_lite.utils.tkinter.menu import parse_menu_label

st = scope("entry_widget")


def boolean_to_state(state: bool) -> Literal["normal", "disabled"]:
    return "normal" if state else "disabled"


def state_to_boolean(state: Literal["normal", "disabled"]) -> bool:
    return state == "normal"


class TextContextMenu(Menu):
    master: Text | Entry

    def __init__(self, master: Text | Entry, **kw):
        super().__init__(master, tearoff=False, **kw)

    def is_selected(self):
        try:
            self.master.index(SEL_FIRST)
            return True
        except TclError:
            return False

    def show(self, x: int, y: int):
        self.master.focus()
        self.delete(0, "end")
        state_by_selected = boolean_to_state(self.is_selected())
        is_master_editable = state_to_boolean(self.master.cget("state"))
        if is_master_editable:
            self.add_command(
                **parse_menu_label(st("menu_undo")),
                command=lambda: self.master.event_generate("<<Undo>>"),
            )
            self.add_command(
                **parse_menu_label(st("menu_redo")),
                command=lambda: self.master.event_generate("<<Redo>>"),
            )
            self.add_separator()
            self.add_command(
                **parse_menu_label(st("menu_cut")),
                command=lambda: self.master.event_generate("<<Cut>>"),
                state=state_by_selected,
            )
        self.add_command(
            **parse_menu_label(st("menu_copy")),
            command=lambda: self.master.event_generate("<<Copy>>"),
            state=state_by_selected,
        )
        if is_master_editable:
            self.add_command(
                **parse_menu_label(st("menu_paste")),
                command=lambda: self.master.event_generate("<<Paste>>"),
            )
            self.add_command(
                **parse_menu_label(st("menu_delete")),
                command=lambda: self.master.event_generate("<<Clear>>"),
                state=state_by_selected,
            )
        self.add_separator()
        self.add_command(
            **parse_menu_label(st("menu_select_all")),
            command=lambda: self.master.event_generate("<<SelectAll>>"),
        )
        self.tk_popup(x, y)

    def bind_to_widget(self):
        self.master.bind("<<ContextMenu>>", lambda event: self.show(event.x_root, event.y_root), add="+")
