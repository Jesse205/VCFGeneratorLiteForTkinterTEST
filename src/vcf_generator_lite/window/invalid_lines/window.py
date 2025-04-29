from tkinter import Misc
from tkinter.constants import ACTIVE, BOTH, LEFT, RIGHT, SE, W, X
from tkinter.ttk import Button, Frame, Label, Sizegrip
from typing import override

from vcf_generator_lite.layout.vertical_dialog_layout import VerticalDialogLayout
from vcf_generator_lite.util.tkinter.font import extend_font
from vcf_generator_lite.util.tkinter.widget import auto_wrap_configure_event
from vcf_generator_lite.widget.scrolled_treeview import ScrolledTreeview
from vcf_generator_lite.window.base import ExtendedDialog
from vcf_generator_lite.window.base.constants import EVENT_EXIT


class InvalidLinesWindow(ExtendedDialog, VerticalDialogLayout):

    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.title("生成 VCF 文件完成")
        self.resizable(True, True)
        self.wm_size_pt(375, 300)
        self.wm_minsize_pt(225, 225)
        self._create_widgets(self)
        self.bell()

    @override
    def _create_header(self, parent: Misc):
        header_frame = Frame(parent, style="DialogHeader.TFrame")
        self.header_icon = Label(
            header_frame,
            text="\u26A0",
            font=extend_font("TkDefaultFont", size=24),
            style="DialogHeaderContent.TLabel"
        )
        self.header_icon.pack(side=LEFT, padx="14p", pady="7p")
        self.header_label = Label(header_frame, style="DialogHeaderContent.TLabel")
        self.header_label.bind("<Configure>", auto_wrap_configure_event, "+")
        self.header_label.pack(fill=X, padx=(0, "14p"), pady="14p")
        return header_frame

    @override
    def _create_content(self, parent: Misc):
        content_frame = Frame(parent)
        content_label = Label(content_frame, text="异常的号码：")
        content_label.pack(fill=X, padx="7p", pady=("7p", "2p"))
        self.content_tree = ScrolledTreeview(
            content_frame,
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
        self.content_tree.heading('row', text='位置', anchor=W)
        self.content_tree.heading('context', text='原始内容', anchor=W)
        self.content_tree.pack(fill=BOTH, expand=True, padx="7p")
        return content_frame

    @override
    def _create_actions(self, parent: Misc):
        action_frame = Frame(parent)
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
