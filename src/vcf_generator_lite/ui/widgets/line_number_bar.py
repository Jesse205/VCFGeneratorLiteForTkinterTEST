from tkinter import Event, Misc, Text
from typing import NamedTuple

from vcf_generator_lite.utils.tkinter.text import get_display_lines_fast, select_lines

TAG_LINE_NUMBER = "line_number"
WIDTH_MIN = 2


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
            cursor="right_ptr",
            insertofftime=0,
            padx="1p",
        )
        self._bound_text: BoundText | None = None
        self.__update_display_after: str | None = None
        self.__last_line_texts: list[str] = ["1"]
        self.__last_pressed_row: int | None = None
        self.tag_config(TAG_LINE_NUMBER, justify="right")
        self.insert("1.0", "1")
        self.configure(state="disabled")
        self.bind("<FocusIn>", self.__on_focus_in, "+")
        self.bind("<ButtonPress-1>", self.__on_primary_button_press, "+")
        self.bind("<Button1-Motion>", self.__on_primary_button_motion, "+")
        self.bind("<ButtonRelease-1>", self.__on_primary_button_release, "+")

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
            inactiveselectbackground=background,
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
        self.configure(width=max(len(str(lines)), WIDTH_MIN))

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
            self.tag_add(TAG_LINE_NUMBER, "1.0", "end")
            self.configure(state="disabled")
            self.__last_line_texts = line_texts

        self.update_display_offset()

    def update_display_offset(self):
        if self._bound_text is None:
            return
        first_index_dlineinfo = self._bound_text.widget.dlineinfo("@0,0")
        if first_index_dlineinfo is None:
            return
        self.yview(0)
        self.yview_scroll(-first_index_dlineinfo[1], "pixels")

    def __on_y_scroll_command(self, _: float, __: float):
        if self._bound_text is None:
            return
        self.update_display_offset()

    def __on_text_y_scroll_command(self, start: float, end: float):
        if self._bound_text is None:
            return
        self.tk.call(self._bound_text.yscrollcommand_cmd, start, end)
        self.update_lines()
        self.update_display_debounce()

    def __on_focus_in(self, _: Event):
        if self._bound_text:
            self._bound_text.widget.focus_set()

    def __on_primary_button_press(self, event: Event):
        if self._bound_text is None:
            return
        text_widget = self._bound_text.widget

        self.__last_pressed_row = click_row = int(text_widget.index(f"@{event.x},{event.y}").split(".")[0])
        select_lines(text_widget, click_row, click_row, see=False)

    def __on_primary_button_motion(self, event: Event):
        if self.__last_pressed_row is None or self._bound_text is None:
            return
        text_widget = self._bound_text.widget

        click_row = int(text_widget.index(f"@{event.x},{event.y}").split(".")[0])
        min_row = min(self.__last_pressed_row, click_row)
        max_row = max(self.__last_pressed_row, click_row)
        select_lines(text_widget, min_row, max_row, see=False)

    def __on_primary_button_release(self, _: Event):
        self.__last_pressed_row = None
