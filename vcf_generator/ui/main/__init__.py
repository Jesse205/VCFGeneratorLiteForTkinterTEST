import logging
import re
import webbrowser
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from typing import IO, List

from constants import URL_RELEASES, URL_SOURCE
from vcf_generator import constants
from vcf_generator.ui import about
from vcf_generator.ui.base import BaseWindow
from vcf_generator.util import dialog, vcard
from vcf_generator.util.phone import is_china_phone
from vcf_generator.util.widget import get_auto_wrap_event
from vcf_generator.widget.menu import TextContextMenu
from vcf_generator.widget.scrolledtext import ScrolledText

MAX_INVALID_COUNT = 1000


class MainWindow(BaseWindow):
    generate_button = None
    text_input = None
    text_context_menu = None

    def __init__(self):
        self.controller = MainController(self)
        super().__init__()

    def on_init_widgets(self):
        self.anchor(CENTER)
        self.title(constants.APP_NAME)
        self.set_minsize(200, 400)
        self.set_size(600, 600)
        sizegrip = Sizegrip(self)
        sizegrip.place(relx=1, rely=1, anchor=SE)
        description_label = Label(self, text=constants.USAGE, justify=LEFT)
        description_label.bind("<Configure>", get_auto_wrap_event(description_label, 300))
        description_label.pack(fill=X, padx="10p", pady="10p")
        self.text_input = ScrolledText(self, undo=True, tabs=True, height=0)
        self.text_input.insert(0.0, constants.DEFAULT_INPUT_CONTENT)
        self.text_input.pack(fill=BOTH, expand=True)

        self.text_context_menu = TextContextMenu(self.text_input)
        self.text_context_menu.bind_to_widget()

        self.generate_button = Button(self, text="生成", default=ACTIVE, command=self.controller.generate_file)
        self.generate_button.pack(side=RIGHT, padx="10p", pady="10p")

    def on_init_menus(self, menu_bar: Menu):
        file_menu = Menu(menu_bar, tearoff=False)
        file_menu.add_command(
            label="退出",
            command=self.quit,
            accelerator="Alt + F4"
        )
        menu_bar.add_cascade(label="文件", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=False)
        edit_menu.add_command(
            label='剪切',
            command=self.text_context_menu.cut,
            accelerator="Ctrl + X",
        )
        edit_menu.add_command(
            label='复制',
            command=self.text_context_menu.copy,
            accelerator="Ctrl + C",
        )
        edit_menu.add_command(
            label='粘贴',
            command=self.text_context_menu.paste,
            accelerator="Ctrl + V"
        )
        edit_menu.add_command(
            label='删除',
            command=self.text_context_menu.clear,
            accelerator="Ctrl + D",
        )
        menu_bar.add_cascade(label="编辑", menu=edit_menu)

        tool_menu = Menu(menu_bar, tearoff=False)
        tool_menu.add_command(
            label="移除引号",
            command=self.controller.on_clean_quotes_click
        )
        menu_bar.add_cascade(label="工具", menu=tool_menu)

        help_menu = Menu(menu_bar, tearoff=False)
        help_menu.add_command(
            label="源代码",
            command=lambda: webbrowser.open(URL_SOURCE)
        )
        help_menu.add_command(
            label="版本发布",
            command=lambda: webbrowser.open(URL_RELEASES)
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="关于",
            command=self.controller.show_about_dialog
        )
        menu_bar.add_cascade(label="帮助", menu=help_menu)


class MainController:
    def __init__(self, window: MainWindow):
        self.window = window

    def _get_text_content(self):
        return self.window.text_input.get(1.0, END)[:-1]  # 获取到的字符串末尾会有一个换行符，所以要消掉

    def _set_text_content(self, new_content):
        self.window.text_input.delete(1.0, END)
        self.window.text_input.replace(1.0, END, new_content)

    def generate_file(self):
        text_content = self._get_text_content()
        logging.info("Start generate vcf file.")
        file_io = filedialog.asksaveasfile(parent=self.window, initialfile="phones.vcf",
                                           filetypes=[("vCard 文件", ".vcf")], defaultextension=".vcf")
        if file_io is None:
            return
        invalid_lines = MainController.generate_content(file_io, text_content)
        if len(invalid_lines) > 0:
            MainController.show_invalid_lines_dialog(invalid_lines)
        dialog.show_info("生成 VCF 文件完成", f"已导出文件到 \"{file_io.name}\"。")
        logging.info("Generate file successfully.")

    @staticmethod
    def generate_content(str_io: IO, text_content: str):
        logging.info("Start generate content.")
        invalid_lines: List[str] = []
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
                logging.error(f"Contact not recognized: '{line_text}'", )
                invalid_lines.append(line_text)
                continue
            name, phone = person_info[0].strip(), person_info[1].strip()
            if not phone.isnumeric() or not is_china_phone(phone):
                logging.error(f"The phone number is illegal: '{line_text}'.")
                invalid_lines.append(line_text)
                continue
            str_io.write(f"{vcard.get_vcard_item_content(name, int(phone))}\n\n")
        logging.info("Generation complete.")
        return invalid_lines

    @staticmethod
    def show_invalid_lines_dialog(invalid_lines: List[str]):
        count = len(invalid_lines)
        message = f"以下电话号码无法识别：\n{', '.join(invalid_lines[0:MAX_INVALID_COUNT])}"
        if count > MAX_INVALID_COUNT:
            message += f"... 等{count - MAX_INVALID_COUNT}个。"
        dialog.show_error("无法识别电话号码", message)

    def show_about_dialog(self):
        about.AboutWindow(self.window)

    def _clean_quotes(self):
        origin_content = self._get_text_content()
        result_content = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r'\1', origin_content, flags=re.S)
        self._set_text_content(result_content)

    def on_clean_quotes_click(self):
        self._clean_quotes()


def main():
    window = MainWindow()
    window.mainloop()


if __name__ == '__main__':
    main()
