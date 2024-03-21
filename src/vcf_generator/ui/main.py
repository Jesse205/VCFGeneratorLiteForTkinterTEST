from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from typing import IO

from vcf_generator import constants
from vcf_generator.ui.base import BaseWindow
from vcf_generator.util import logger, dialog, vcard
from vcf_generator.util.widget import get_auto_wrap_event

MAX_INVALID_COUNT = 1000

LabeledScale

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.title(constants.APP_NAME)
        self.set_minsize(200, 400)
        self.set_size(600, 600)
        sizegrip = Sizegrip(self)
        sizegrip.place(relx=1, rely=1, anchor=SE)
        description_label = Label(self, text=constants.USAGE, justify=LEFT)
        description_label.bind("<Configure>", get_auto_wrap_event(description_label, 300))
        description_label.pack(fill=X, padx=10, pady=10)
        self.text_input = ScrolledText(self, undo=True, tabs=True, height=0, borderwidth=0)
        self.text_input.insert(0.0, constants.DEFAULT_INPUT_CONTENT)
        self.text_input.pack(fill=BOTH, expand=True)
        self.generate_button = Button(self, text="生成", default=ACTIVE)
        self.generate_button.pack(padx=10, pady=10, side=RIGHT)


class MainController:
    def __init__(self, window: MainWindow):
        self.window = window
        window.generate_button.configure(command=self.generate_file)

    def generate_file(self):
        text_content = self.window.text_input.get(0.0, "end")
        logger.info("Start generate vcf file.")
        file_io = filedialog.asksaveasfile(parent=self.window, initialfile="phones.vcf",
                                           filetypes=[("vCard 文件", ".svf")], defaultextension=".svf")
        if file_io is None:
            return
        invalid_lines = MainController.generate_content(file_io, text_content)
        if len(invalid_lines) > 0:
            MainController.show_invalid_lines_dialog(invalid_lines)
        dialog.show_info("生成 VCF 文件完成", f"已导出文件到 \"{file_io.name}\"。")
        logger.info("Generate file successfully.")

    @staticmethod
    def generate_content(str_io: IO, text_content: str):
        logger.info("Start generate content.")
        invalid_lines: list[str] = []
        # 将制表符转换为空格，统一处理
        text_content = text_content.replace("\t", " ")
        for line_text in text_content.split("\n"):
            line_text = line_text.strip()
            # 空行跳过
            if line_text == "":
                continue
            person_info = line_text.rsplit(" ", 1)
            # 虽然是分割一次，但是用户可能不会输入空格。这时候会出现错误。
            if len(person_info) != 2:
                logger.error("联系人无法识别", f'"{line_text}"')
                invalid_lines.append(line_text)
                continue
            name, phone = person_info[0].strip(), person_info[1].strip()
            if not phone.isnumeric():
                logger.error("电话号码不合法", f'"{line_text}"')
                invalid_lines.append(line_text)
                continue
            str_io.write(f"{vcard.get_vcard_item_content(name, int(phone))}\n\n")
        logger.info("Generation complete.")
        return invalid_lines

    @staticmethod
    def show_invalid_lines_dialog(invalid_lines: list[str]):
        count = len(invalid_lines)
        message = f"以下电话号码无法识别：\n{', '.join(invalid_lines[0:MAX_INVALID_COUNT])}"
        if count > MAX_INVALID_COUNT:
            message += f"... 等{count - MAX_INVALID_COUNT}个。"
        dialog.show_error("无法识别电话号码", message)


def main():
    window = MainWindow()
    MainController(window)
    window.mainloop()
