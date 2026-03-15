from tkinter import Misc
from tkinter.ttk import Button, Frame, Label, Separator, Sizegrip
from typing import override

from vcf_generator_lite.ui.layouts.vertical_dialog_layout import VerticalDialogLayout
from vcf_generator_lite.utils.locales import t
from vcf_generator_lite.utils.tkinter.font import extend_font_scale
from vcf_generator_lite.utils.tkinter.misc import scale_kw
from vcf_generator_lite.utils.tkinter.widget import enable_auto_wrap
from vcf_generator_lite.ui.widgets.scrolled_treeview import ScrolledTreeview
from vcf_generator_lite.ui.windows.base_window import EnhancedDialog
from vcf_generator_lite.ui.windows.base_window.constants import EVENT_EXIT
from vcf_generator_lite.ui.windows.invalid_items_dialog.common import st


class InvalidItemsDialog(EnhancedDialog, VerticalDialogLayout):
    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.title(st("title"))
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
            text="\u26a0",
            font=extend_font_scale("TkDefaultFont", 24 / 9),
            style="DialogHeaderContent.TLabel",
            foreground="orange",
        )
        self.header_icon.pack(side="left", padx="14p", pady="7p")
        self.header_label = Label(header_frame, style="DialogHeaderContent.TLabel")
        enable_auto_wrap(self.header_label)
        self.header_label.pack(fill="x", padx=(0, "14p"), pady="14p")
        return header_frame

    @override
    def _create_content(self, parent: Misc):
        Separator(parent).pack(fill="x")
        content_frame = Frame(parent)
        content_label = Label(content_frame, text=st("label_invalid_numbers"))
        content_label.pack(fill="x", padx="7p", pady=("7p", "2p"))
        self.content_tree = ScrolledTreeview(
            content_frame,
            columns=("row", "original", "reason"),
            show="headings",
            selectmode="browse",
            height=0,
        )
        self.content_tree.column(
            column="row",
            anchor="w",
            stretch=False,
            **scale_kw(
                self,
                width=60,
                minwidth=45,
            ),
        )
        self.content_tree.column("original", anchor="w")
        self.content_tree.heading("row", text=st("heading_row"), anchor="w")
        self.content_tree.heading("original", text=st("heading_original"), anchor="w")
        self.content_tree.heading("reason", text=st("heading_reason"), anchor="w")
        self.content_tree.pack(fill="both", expand=True, padx="7p")
        return content_frame

    @override
    def _create_footer(self, parent: Misc):
        footer_frame = Frame(parent)
        sizegrip = Sizegrip(footer_frame)
        sizegrip.place(relx=1, rely=1, anchor="se")
        self.ok_button = Button(
            footer_frame,
            text=t("button_ok"),
            default="active",
            command=lambda: self.event_generate(EVENT_EXIT),
        )
        self.ok_button.pack(side="right", padx="7p", pady="7p")
        return footer_frame
