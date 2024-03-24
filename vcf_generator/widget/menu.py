from tkinter import *
from typing import Union, Literal


class TextContextMenu(Menu):
    master: Union[Text, Entry]

    def __init__(self, master: Union[Text, Entry], **kw):
        super().__init__(master, tearoff=False, **kw,)

    def is_selected(self):
        try:
            self.master.index(SEL_FIRST)
            return True
        except TclError:
            return False

    def cut(self):
        self.master.event_generate("<<Cut>>")

    def copy(self):
        self.master.event_generate("<<Copy>>")

    def paste(self):
        self.master.event_generate('<<Paste>>')

    def clear(self):
        self.master.event_generate("<<Clear>>")

    def show(self, x: int, y: int):
        is_selected = self.is_selected()
        menu_state_with_selected: Literal["normal", "disabled"] = "normal" if is_selected else "disabled"
        self.delete(0, END)
        self.add_command(
            label='剪切',
            command=lambda: self.cut(),
            accelerator="Ctrl + X",
            state=menu_state_with_selected
        )
        self.add_command(
            label='复制',
            command=lambda: self.copy(),
            accelerator="Ctrl + C",
            state=menu_state_with_selected
        )
        self.add_command(
            label='粘贴',
            command=lambda: self.paste(),
            accelerator="Ctrl + V"
        )
        self.add_command(
            label='删除',
            command=lambda: self.clear(),
            accelerator="Ctrl + D",
            state=menu_state_with_selected
        )
        # self.add_command(label='全选', command=lambda: self.select_all())
        self.post(x, y)

    def bind_to_widget(self):
        self.master.bind("<Button-3>", lambda event: self.show(event.x_root, event.y_root))
