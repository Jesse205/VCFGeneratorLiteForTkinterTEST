import dataclasses
from tkinter.ttk import Scrollbar, Style, Treeview

from vcf_generator_lite.utils.graphics import FPixelPadding, parse_padding
from vcf_generator_lite.utils.tkinter.misc import scale


class ScrolledTreeview(Treeview):
    def __init__(self, master=None, vertical=True, **kw):
        super().__init__(master, **kw)
        self.vbar: Scrollbar | None = None
        self._insets: FPixelPadding = FPixelPadding()

        if vertical:
            self._create_vertical_scrollbar()

    @property
    def insets(self) -> FPixelPadding:
        return self._insets

    @insets.setter
    def insets(self, insets: FPixelPadding):
        previous_insets = self._insets
        padding = self._get_current_padding()
        new_padding = padding - previous_insets + insets
        self.configure(padding=new_padding.to_tuple())
        self._insets = insets

    def _create_vertical_scrollbar(self):
        if not self.vbar:
            self.vbar = Scrollbar(self, orient="vertical")
            self.vbar.pack(side="right", fill="y", pady="1.5p", padx="1.5p")
            self.configure(yscrollcommand=self.vbar.set)
            self.insets = dataclasses.replace(
                self._insets,
                right=self.vbar.winfo_reqwidth() + scale(self, 1.5),
            )
            self.vbar.configure(command=self.yview)

    def _get_current_padding(self) -> FPixelPadding:
        padding = self.cget("padding")
        if not padding:
            padding = Style(self).lookup(self.cget("style") or "Treeview", "padding")
        if not padding:
            padding = 0
        return parse_padding(self, padding)
