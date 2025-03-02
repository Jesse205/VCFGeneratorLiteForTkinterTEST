from tkinter import Event

from vcf_generator_lite.util.vcard import InvalidLine
from vcf_generator_lite.window.invalid_lines.window import InvalidLinesWindow

message_invalid_template = "已导出文件到 {path}，但部分异常的号码未包含在导出文件中。"
invalid_line_position_template = "第 {row} 行"
invalid_line_template = "第 {row_position} 行：{content}"
ignored_template = "{content}... 等 {ignored_count} 个。"


class InvalidLinesController:
    def __init__(self, window: InvalidLinesWindow, display_path: str,
                 invalid_lines: list[InvalidLine], ):
        self.window = window
        window.bind("<Return>", self.on_ok_click)
        window.header_label.configure(text=message_invalid_template.format(path=display_path))
        for item in invalid_lines:
            window.treeview.insert(
                '',
                'end',
                text=invalid_line_position_template.format(row=item.row_position + 1),
                values=(item.content,)
            )

    def on_ok_click(self, _: Event):
        self.window.ok_button.invoke()
