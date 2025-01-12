import re
import webbrowser
from concurrent.futures import Future
from tkinter import filedialog, Menu, Event
from tkinter.constants import *
from tkinter.ttk import *

from vcf_generator.constants import URL_RELEASES, URL_SOURCE, APP_NAME, DEFAULT_INPUT_CONTENT, USAGE
from vcf_generator.ui.about import open_about_window
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
        self.text_input.pack(fill=BOTH, expand=True, padx="10p", pady=0)
        self.text_context_menu = TextContextMenu(self.text_input)
        self.text_context_menu.bind_to_widget()

        bottom_frame = Frame(self)
        bottom_frame.pack(fill=X)

        sizegrip = Sizegrip(bottom_frame)
        sizegrip.place(relx=1, rely=1, anchor=SE)

        self.progress_bar = Progressbar(bottom_frame, orient=HORIZONTAL, length=200, mode='determinate', maximum=1)

        self.generate_button = Button(bottom_frame, text="生成(G)", default=ACTIVE,
                                      command=lambda: self.event_generate(EVENT_ON_GENERATE_CLICK), underline=3)
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
            label="退出(X)",
            command=self.quit,
            accelerator="Alt + F4",
            underline=3,
        )
        menu_bar.add_cascade(label="文件(F)", menu=file_menu, underline=3)

        edit_menu = Menu(menu_bar, tearoff=False)
        edit_menu.add_command(
            label='剪切(T)',
            command=lambda: self.focus_get().event_generate("<<Cut>>"),
            accelerator="Ctrl + X",
            underline=3,
        )
        edit_menu.add_command(
            label='复制(C)',
            command=lambda: self.focus_get().event_generate("<<Copy>>"),
            accelerator="Ctrl + C",
            underline=3,
        )
        edit_menu.add_command(
            label='粘贴(P)',
            command=lambda: self.focus_get().event_generate("<<Paste>>"),
            accelerator="Ctrl + V",
            underline=3,
        )
        edit_menu.add_command(
            label='删除(D)',
            command=lambda: self.focus_get().event_generate("<<Clear>>"),
            accelerator="Ctrl + D",
            underline=3,
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="移除引号",
            command=lambda: self.event_generate(EVENT_ON_CLEAN_QUOTES_CLICK)
        )
        menu_bar.add_cascade(label="编辑(E)", menu=edit_menu, underline=3)

        help_menu = Menu(menu_bar, tearoff=False)
        help_menu.add_command(
            label="VCF 生成器 Lite 源代码网址",
            command=lambda: webbrowser.open(URL_SOURCE)
        )
        help_menu.add_command(
            label="VCF 生成器 Lite 发布网址",
            command=lambda: webbrowser.open(URL_RELEASES)
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="关于 VCF 生成器 Lite(A)",
            command=lambda: self.event_generate(EVENT_ON_ABOUT_CLICK),
            underline=16,
        )
        menu_bar.add_cascade(label="帮助(H)", menu=help_menu, underline=3)


class MainController:
    _previous_update_progress_id: str = None

    def __init__(self, window: MainWindow):
        self.window = window
        window.bind(EVENT_ON_ABOUT_CLICK, self.on_about_click)
        window.bind(EVENT_ON_CLEAN_QUOTES_CLICK, self.on_clean_quotes_click)
        window.bind(EVENT_ON_GENERATE_CLICK, self.on_generate_click)
        window.bind("<Return>", self.on_return_click)

    def _get_text_content(self):
        return self.window.text_input.get(1.0, END)[:-1]  # 获取到的字符串末尾会有一个换行符，所以要消掉

    def _set_text_content(self, new_content):
        self.window.text_input.replace(1.0, END, new_content)

    def on_about_click(self, _):
        open_about_window(self.window)

    def on_clean_quotes_click(self, _):
        self._clean_quotes()

    def on_return_click(self, event: Event):
        if event.widget is self.window.text_input:
            return
        self.window.generate_button.invoke()

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
            self._show_generate_done_dialog(file_io.name, future.result().invalid_items)
            self.window.hide_progress_bar()
            self.window.enable_generate_button()

        process_future: Future[GenerateResult] = cpu_executor.submit(generate_vcard_file, file_io, text_content,
                                                                     on_update_progress=update_progress)
        process_future.add_done_callback(lambda future: self.window.after_idle(done, future))

    def _show_generate_done_dialog(self, display_path: str, invalid_items: list[LineContent]):
        title = "生成 VCF 文件完成"
        if len(invalid_items) > 0:
            invalid_text = '，'.join(
                [f"第 {item.line} 行：{item.content}" for item in invalid_items[0:MAX_INVALID_COUNT]])
            ignored_count = max(len(invalid_items) - MAX_INVALID_COUNT, 0)
            if ignored_count > 0:
                invalid_text += f"... 等 {ignored_count} 个。"
            message = "以下电话号码无法识别：\n{invalid_text}\n\n已导出文件到 {display_path}，但异常的号码未包含在此的文件中。".format(
                invalid_text=invalid_text,
                display_path=display_path
            )
            dialog.show_warning(self.window, title, message)
        else:
            dialog.show_info(self.window, title, f'已导出文件到“{display_path}”。')

    def _clean_quotes(self):
        origin_content = self._get_text_content()
        result_content = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r'\1', origin_content, flags=re.S)
        self._set_text_content(result_content)


def create_main_window() -> tuple[MainWindow, MainController]:
    window = MainWindow()
    controller = MainController(window)
    return window, controller
