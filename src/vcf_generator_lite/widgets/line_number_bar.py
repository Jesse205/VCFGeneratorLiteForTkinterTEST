from tkinter import Event, Misc, Text
from typing import NamedTuple

from vcf_generator_lite.utils.tkinter.text import get_display_lines_fast


class BoundText(NamedTuple):
    widget: Text
    yscrollcommand_cmd: str | None


class LineNumberBar(Text):
    def __init__(self, master: Misc | None = None):
        super().__init__(
            master,
            height=0,
            relief="flat",
            exportselection=False,
            takefocus=False,
            foreground="gray",
            selectforeground="gray",
            yscrollcommand=self.__on_y_scroll_command,
        )
        self._bound_text: BoundText | None = None
        self.__update_display_after: str | None = None
        self.__last_line_texts: list[str] = ["1"]
        self.insert("1.0", "1")
        self.configure(state="disabled")

    def bind_text(self, text_widget: Text):
        self._bound_text = BoundText(
            widget=text_widget,
            yscrollcommand_cmd=text_widget["yscrollcommand"],
        )
        self.update_style()
        self.update_lines()
        self.update_display_debounce()
        text_widget.bind("<<WidgetViewSync>>", self.__on_text_widget_view_sync, "+")
        text_widget.bind("<<ThemeChanged>>", self.__on_text_theme_changed, "+")
        text_widget.configure(yscrollcommand=self.__on_text_y_scroll_command)

    def __on_text_theme_changed(self, _: Event):
        self.update_style()

    def update_style(self):
        if self._bound_text is None:
            return
        text_widget = self._bound_text.widget
        background = text_widget["background"]
        self.configure(
            font=text_widget["font"],
            background=background,
            selectbackground=background,
            borderwidth=text_widget["borderwidth"],
            highlightthickness=text_widget["highlightthickness"],
            highlightcolor=background,
            highlightbackground=background,
        )

    def __on_text_widget_view_sync(self, _: Event):
        self.update_lines()
        self.update_display_debounce()

    def update_lines(self):
        if self._bound_text is None:
            return
        lines = int(self._bound_text.widget.index("end").split(".")[0]) - 1
        self.configure(width=len(str(lines)))

    def update_display_debounce(self):
        if self.__update_display_after:
            self.after_cancel(self.__update_display_after)
        self.__update_display_after = self.after_idle(self.update_display)

    def update_display(self):
        if self._bound_text is None:
            return
        text_widget = self._bound_text.widget

        first_index = text_widget.index("@0,0")
        last_index = text_widget.index(f"@0,{text_widget.winfo_height() - 1}")

        first_row = int(first_index.split(".")[0])
        first_column = int(first_index.split(".")[1])
        last_row = int(last_index.split(".")[0])

        line_texts: list[str] = []
        for row in range(first_row, last_row + 1):
            if row > first_row or first_column == 0:
                line_texts.append(str(row))
            else:
                line_texts.append("")
            display_lines = get_display_lines_fast(
                text_widget,
                first_index if row == first_row else f"{row}.0",
                last_index if row == last_row else f"{row}.end",
            )
            if display_lines > 0:
                line_texts.append("\n" * (display_lines - 1))

        if line_texts != self.__last_line_texts:
            self.configure(state="normal")
            self.replace("1.0", "end", "\n".join(line_texts))
            self.configure(state="disabled")
            self.__last_line_texts = line_texts

        self.update_display_offset()

    def update_display_offset(self):
        if self._bound_text is None:
            return
        first_index_dlineinfo = self._bound_text.widget.dlineinfo("@0,0")
        first_index_y = first_index_dlineinfo[1] if first_index_dlineinfo else 0
        self.yview(0)
        self.yview_scroll(-first_index_y, "pixels")

    def __on_y_scroll_command(self, start: float, end: float):
        if self._bound_text is None:
            return
        self.update_display_offset()

    def __on_text_y_scroll_command(self, start: float, end: float):
        if self._bound_text is None:
            return
        self.tk.call(self._bound_text.yscrollcommand_cmd, start, end)
        self.update_display_debounce()
