from tkinter.ttk import Treeview, Scrollbar, Style
from typing import Optional

from vcf_generator_lite.util.tkinter.misc import ScalingMiscExtension


class ScrolledTreeview(Treeview, ScalingMiscExtension):

    def __init__(self, master=None, vertical=True, **kw):
        super().__init__(master, **kw)
        self.vbar: Optional[Scrollbar] = None
        self._previous_avoid_padding: tuple[int, int, int, int] = (0, 0, 0, 0)

        if vertical:
            self._create_vertical_scrollbar()

    def _create_vertical_scrollbar(self):
        if not self.vbar:
            self.vbar = Scrollbar(self, orient="vertical")
            self.vbar.pack(side="right", fill="y", pady="1.5p", padx="1.5p")
            self.configure(yscrollcommand=self.vbar.set)
            self.apply_padding(right=self.vbar.winfo_reqwidth() + self.get_scaled(1.5))
            self.vbar.configure(command=self.yview)

    def apply_padding(
        self,
        *,
        left: Optional[int | float | str] = None,
        top: Optional[int | float | str] = None,
        right: Optional[int | float | str] = None,
        bottom: Optional[int | float | str] = None
    ):
        avoid_padding = (
            left if left is not None else 0,
            top if top is not None else 0,
            right if right is not None else 0,
            bottom if bottom is not None else 0
        )
        padding = self._get_widget_padding()
        self.configure(padding=(
            padding[0] - self._previous_avoid_padding[0] + avoid_padding[0],
            padding[1] - self._previous_avoid_padding[1] + avoid_padding[1],
            padding[2] - self._previous_avoid_padding[2] + avoid_padding[2],
            padding[3] - self._previous_avoid_padding[3] + avoid_padding[3],
        ))
        self._previous_avoid_padding = avoid_padding

    def _get_widget_padding(self):
        style = self.cget("style") or "Treeview"
        padding = self.cget("padding") or Style(self).lookup(style, "padding") or (0,)
        left = self.parse_dimen(str(padding[0])) if len(padding) >= 1 else 0
        top = self.parse_dimen(str(padding[1])) if len(padding) >= 2 else left
        right = self.parse_dimen(str(padding[2])) if len(padding) >= 3 else left
        bottom = self.parse_dimen(str(padding[3])) if len(padding) >= 4 else top
        return left, top, right, bottom
