from tkinter import *
from typing import Union, Literal


def boolean_to_state(state: bool) -> Literal["normal", "disabled"]:
    return "normal" if state else "disabled"


def state_to_boolean(state: Literal["normal", "disabled"]) -> bool:
    return state == "normal"


class TextContextMenu(Menu):
    master: Union[Text, Entry]

    def __init__(self, master: Union[Text, Entry], **kw):
        super().__init__(master, tearoff=False, **kw)

    def is_selected(self):
        try:
            self.master.index(SEL_FIRST)
            return True
        except TclError:
            return False

    def show(self, x: int, y: int):
        state_by_selected = boolean_to_state(self.is_selected())
        is_master_editable = state_to_boolean(self.master.cget("state"))
        self.delete(0, END)
        if is_master_editable:
            self.add_command(
                label='撤消(U)',
                command=lambda: self.master.event_generate("<<Undo>>"),
                underline=3,
            )
            self.add_separator()
            self.add_command(
                label='剪切(T)',
                command=lambda: self.master.event_generate("<<Cut>>"),
                state=state_by_selected,
                underline=3,
            )
        self.add_command(
            label='复制(C)',
            command=lambda: self.master.event_generate("<<Copy>>"),
            state=state_by_selected,
            underline=3,
        )
        if is_master_editable:
            self.add_command(
                label='粘贴(P)',
                command=lambda: self.master.event_generate("<<Paste>>"),
                underline=3,
            )
            self.add_command(
                label='删除(D)',
                command=lambda: self.master.event_generate("<<Clear>>"),
                state=state_by_selected,
                underline=3,
            )
        self.add_separator()
        self.add_command(
            label='全选(A)',
            command=lambda: self.master.event_generate("<<SelectAll>>"),
            underline=3,
        )
        self.post(x, y)

    def bind_to_widget(self):
        self.master.bind("<Button-3>", lambda event: self.show(event.x_root, event.y_root), add="+")
