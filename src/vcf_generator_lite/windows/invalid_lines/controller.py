from tkinter import Event

from vcf_generator_lite.core.vcf_generator import InvalidLine
from vcf_generator_lite.windows.invalid_lines.window import InvalidLinesWindow

message_invalid_template = "已导出文件到 {path}，异常的号码已被忽略。"
invalid_line_position_template = "第 {row} 行"


class InvalidLinesController:
    def __init__(
        self,
        window: InvalidLinesWindow,
        display_path: str,
        invalid_lines: list[InvalidLine],
    ):
        self.window = window
        window.bind("<Return>", self.on_ok_click)
        window.header_label.configure(text=message_invalid_template.format(path=display_path))
        for item in invalid_lines:
            window.content_tree.insert(
                parent="",
                index="end",
                id=item.row_position,
                values=(
                    invalid_line_position_template.format(row=item.row_position + 1),
                    item.content,
                ),
            )

    def on_ok_click(self, _: Event):
        self.window.ok_button.invoke()
