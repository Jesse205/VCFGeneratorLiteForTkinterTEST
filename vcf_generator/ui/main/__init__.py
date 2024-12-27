import re
import webbrowser
from concurrent.futures import Future
from tkinter import filedialog, Menu
from tkinter.constants import *
from tkinter.ttk import *

from vcf_generator.constants import URL_RELEASES, URL_SOURCE, APP_NAME, DEFAULT_INPUT_CONTENT, USAGE
from vcf_generator.ui.about import create_about_window
from vcf_generator.ui.base import BaseWindow
from vcf_generator.util import dialog
from vcf_generator.util.thread import cpu_executor
from vcf_generator.util.vcard import generate_vcard_file, LineContent, GenerateResult
from vcf_generator.util.widget import get_auto_wrap_event
from vcf_generator.widget.menu import TextContextMenu
from vcf_generator.widget.scrolledtext import ScrolledText

MAX_INVALID_COUNT = 200

EVENT_ON_ABOUT_CLICK = "<<OnAboutClick>>"
EVENT_ON_CLEAN_QUOTES_CLICK = "<<OnCleanQuotesClick>>"
EVENT_ON_GENERATE_CLICK = "<<OnGenerateClick>>"


class MainWindow(BaseWindow):
    generate_button = None
    text_input = None
    text_context_menu = None
    progress_bar = None

    def on_init_window(self):
        self.anchor(CENTER)
        self.title(APP_NAME)
        self.set_minsize(400, 400)
        self.set_size(600, 600)

    def on_init_widgets(self):
        description_label = Label(self, text=USAGE, justify=LEFT)
        description_label.bind("<Configure>", get_auto_wrap_event(description_label))
        description_label.pack(fill=X, padx="10p", pady="10p")
        self.text_input = ScrolledText(self, undo=True, tabs=True, height=0)
        self.text_input.insert(0.0, DEFAULT_INPUT_CONTENT)
        self.text_input.edit_reset()
        self.text_input.pack(fill=BOTH, expand=True)
        self.text_context_menu = TextContextMenu(self.text_input)
        self.text_context_menu.bind_to_widget()

        bottom_frame = Frame(self)
        bottom_frame.pack(fill=X)

        sizegrip = Sizegrip(bottom_frame)
        sizegrip.place(relx=1, rely=1, anchor=SE)

        self.progress_bar = Progressbar(bottom_frame, orient=HORIZONTAL, length=200, mode='determinate', maximum=1)

        self.generate_button = Button(bottom_frame, text="生成", default=ACTIVE,
                                      command=lambda: self.event_generate(EVENT_ON_GENERATE_CLICK))
        self.generate_button.pack(side=RIGHT, padx="10p", pady="10p")

    def show_progress_bar(self):
        self.progress_bar.pack(side=LEFT, padx="10p", pady="10p")

    def hide_progress_bar(self):
        self.progress_bar.pack_forget()

    def set_progress(self, progress: float):
        self.progress_bar.configure(value=progress)

    def enable_generate_button(self):
        self.generate_button.configure(state=NORMAL)

    def disable_generate_button(self):
        self.generate_button.configure(state=DISABLED)

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
            command=lambda: self.event_generate(EVENT_ON_CLEAN_QUOTES_CLICK)
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
            command=lambda: self.event_generate(EVENT_ON_ABOUT_CLICK)
        )
        menu_bar.add_cascade(label="帮助", menu=help_menu)


class MainController:
    _previous_update_progress_id: str = None

    def __init__(self, window: MainWindow):
        self.window = window
        window.bind(EVENT_ON_ABOUT_CLICK, self.on_about_click)
        window.bind(EVENT_ON_CLEAN_QUOTES_CLICK, self.on_clean_quotes_click)
        window.bind(EVENT_ON_GENERATE_CLICK, self.on_generate_click)

    def _get_text_content(self):
        return self.window.text_input.get(1.0, END)[:-1]  # 获取到的字符串末尾会有一个换行符，所以要消掉

    def _set_text_content(self, new_content):
        self.window.text_input.replace(1.0, END, new_content)

    def on_about_click(self, _):
        create_about_window(self.window)

    def on_clean_quotes_click(self, _):
        self._clean_quotes()

    def on_generate_click(self, _):
        text_content = self._get_text_content()
        file_io = filedialog.asksaveasfile(parent=self.window, initialfile="phones.vcf",
                                           filetypes=[("vCard 文件", ".vcf")], defaultextension=".vcf")
        if file_io is None:
            return

        self.window.show_progress_bar()
        self.window.set_progress(0)
        self.window.disable_generate_button()

        def update_progress(progress):
            if self._previous_update_progress_id is not None:
                self.window.after_cancel(self._previous_update_progress_id)
            self._previous_update_progress_id = self.window.after_idle(self.window.set_progress, progress)

        def done(future: Future[GenerateResult]):
            if len(future.result().invalid_items) > 0:
                MainController.show_invalid_items_dialog(future.result().invalid_items)
            dialog.show_info("生成 VCF 文件完成", f"已导出文件到 \"{file_io.name}\"。")
            self.window.hide_progress_bar()
            self.window.enable_generate_button()

        process_future: Future[GenerateResult] = cpu_executor.submit(generate_vcard_file, file_io, text_content,
                                                                     on_update_progress=update_progress)
        process_future.add_done_callback(lambda future: self.window.after_idle(done, future))

    @staticmethod
    def show_invalid_items_dialog(invalid_items: list[LineContent]):
        count = len(invalid_items)
        invalid_text_list = [f"第 {item.line} 行：{item.content}" for item in invalid_items[0:MAX_INVALID_COUNT]]
        message = "以下电话号码无法识别：\n{content}".format(content='，'.join(invalid_text_list))
        if count > MAX_INVALID_COUNT:
            message += f"... 等 {count - MAX_INVALID_COUNT} 个。"
        dialog.show_error("出现无法识别电话号码", message)

    def _clean_quotes(self):
        origin_content = self._get_text_content()
        result_content = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r'\1', origin_content, flags=re.S)
        self._set_text_content(result_content)


def create_main_window() -> tuple[MainWindow, MainController]:
    window = MainWindow()
    controller = MainController(window)
    return window, controller
