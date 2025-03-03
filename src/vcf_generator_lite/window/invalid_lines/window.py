from tkinter import Misc, Label as TkLabel
from tkinter.constants import X, ACTIVE, RIGHT, BOTTOM, BOTH, W, SE, LEFT
from tkinter.ttk import Frame, Label, Button, Sizegrip, Style
from typing import override

from vcf_generator_lite.util.tkinter.widget import auto_wrap_configure_event
from vcf_generator_lite.widget.scrolled_treeview import ScrolledTreeview
from vcf_generator_lite.window.base import ExtendedDialog
from vcf_generator_lite.window.base.constants import EVENT_EXIT

title_invalid = "生成 VCF 文件完成"


class InvalidLinesWindow(ExtendedDialog):

    @override
    def on_init_window(self):
        super().on_init_window()
        self.title(title_invalid)
        self.resizable(True, True)
        self.wm_size_pt(375, 300)
        self.wm_minsize_pt(225, 225)
        self._create_widgets()
        self.bell()

    def _create_widgets(self):
        header_frame = self._create_header(self)
        header_frame.pack(fill=X)
        content_label = Label(self, text="异常的号码：")
        content_label.pack(fill=X, padx="7p", pady=("7p", "2p"))
        self.content_tree = ScrolledTreeview(
            self,
            columns=("row", "context"),
            show='headings',
            selectmode="browse"
        )
        self.content_tree.column(
            column='row',
            anchor=W,
            stretch=False,
            width=self.get_scaled(60),
            minwidth=self.get_scaled(45)
        )
        self.content_tree.column('context', anchor=W)
        self.content_tree.heading('row', text='行数', anchor=W)
        self.content_tree.heading('context', text='原始内容', anchor=W)
        self.content_tree.pack(fill=BOTH, expand=True, padx="7p")
        action_frame = self._create_action_bar(self)
        action_frame.pack(fill=X, side=BOTTOM)

    def _create_header(self, master: Misc):
        header_frame = Frame(master, style="InfoHeader.TFrame")
        background_color = Style(master).lookup("InfoHeader.TFrame", "background")
        self.header_icon = TkLabel(header_frame, bitmap="warning", background=background_color)
        self.header_icon.pack(side=LEFT, padx="14p", pady="7p")
        self.header_label = Label(header_frame, style="InfoHeaderContent.TLabel")
        self.header_label.bind("<Configure>", auto_wrap_configure_event, "+")
        self.header_label.pack(fill=X, padx=(0, "14p"), pady="14p")
        return header_frame

    def _create_action_bar(self, master: Misc):
        action_frame = Frame(master)
        sizegrip = Sizegrip(action_frame)
        sizegrip.place(relx=1, rely=1, anchor=SE)
        self.ok_button = Button(
            action_frame,
            text="确定",
            default=ACTIVE,
            command=lambda: self.event_generate(EVENT_EXIT)
        )
        self.ok_button.pack(side=RIGHT, padx="7p", pady="7p")
        return action_frame
