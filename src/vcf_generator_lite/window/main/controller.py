import re
import traceback
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import Event, filedialog

from vcf_generator_lite.util.tkinter import dialog
from vcf_generator_lite.util.vcard import GenerateResult, VCardFileGenerator, InvalidLine
from vcf_generator_lite.window.about import AboutOpener
from vcf_generator_lite.window.base.constants import EVENT_EXIT
from vcf_generator_lite.window.main.constants import EVENT_ABOUT, EVENT_CLEAN_QUOTES, EVENT_GENERATE, MAX_INVALID_COUNT
from vcf_generator_lite.window.main.window import MainWindow


class MainController:
    is_generating = False

    def __init__(self, window: MainWindow):
        self.window = window
        self.about_opener = AboutOpener(window)
        window.bind(EVENT_ABOUT, self.on_about)
        window.bind(EVENT_CLEAN_QUOTES, self.on_clean_quotes)
        window.bind(EVENT_GENERATE, self.on_generate)
        window.bind("<Control-Lock-S>", self.on_generate)
        window.bind("<Control-s>", self.on_generate)
        window.bind("<Return>", self.on_return)
        window.bind(EVENT_EXIT, self.on_exit)

    def on_about(self, _):
        self.about_opener.open()

    def on_clean_quotes(self, _):
        self._clean_quotes()

    def on_return(self, event: Event):
        if event.widget is self.window.text_input:
            return
        self.window.generate_button.invoke()

    def on_generate(self, _):
        text_content = self.window.get_text_content()
        file_io = filedialog.asksaveasfile(
            parent=self.window,
            initialfile="phones.vcf",
            filetypes=[("vCard 文件", ".vcf")],
            defaultextension=".vcf"
        )
        if file_io is None:
            return

        self.is_generating = True
        self.window.show_progress_bar()
        self.window.set_progress(0)
        self.window.set_progress_determinate(False)
        self.window.set_generate_enabled(False)

        def done(future: Future[GenerateResult]):
            file_io.close()
            self._show_generate_done_dialog(file_io.name, future.result())
            self.is_generating = False
            self.window.hide_progress_bar()
            self.window.set_generate_enabled(True)

        def on_update_progress(progress: float, determinate: bool):
            self.window.set_progress_determinate(determinate)
            if determinate:
                self.window.set_progress(progress)

        executor = ThreadPoolExecutor(max_workers=1)
        generator = VCardFileGenerator(executor)
        generator.add_progress_callback(on_update_progress)
        generate_future = generator.start(text_content, file_io)
        generate_future.add_done_callback(done)
        executor.shutdown(wait=False)

    def on_exit(self, _):
        if self.is_generating:
            dialog.show_warning(self.window, "正在生成文件", "文件正在生成中，无法关闭窗口。请稍后重试。")
        else:
            self.window.destroy()

    def _show_generate_done_dialog(self, display_path: str, generate_result: GenerateResult):
        if generate_result.exceptions:
            self._show_generate_error_dialog(generate_result.exceptions)
        elif len(generate_result.invalid_lines) > 0:
            self._show_generate_invalid_dialog(display_path, generate_result.invalid_lines)
        else:
            self._show_generate_success_dialog(display_path)

    def _show_generate_error_dialog(self, exceptions: list[BaseException]):
        title_failure = "生成 VCF 文件失败"
        message_failure_template = "生成 VCF 文件时出现未知异常：\n\n{content}"
        formatted_exceptions = [
            "\n".join(traceback.format_exception(exception)) for exception in exceptions
        ]
        dialog.show_error(self.window, title_failure, message_failure_template.format(
            content="\n\n".join(formatted_exceptions)
        ))

    def _show_generate_invalid_dialog(self, display_path: str, invalid_lines: list[InvalidLine]):
        title_invalid = "生成 VCF 文件部分成功"
        message_invalid_template = "以下电话号码无法识别：\n{content}\n\n已导出文件到 {path}，但异常的号码未包含在导出文件中。"
        invalid_line_template = "第 {row_position} 行：{content}"
        ignored_template = "{content}... 等 {ignored_count} 个。"
        content = '，'.join([
            invalid_line_template.format(row_position=item.row_position, content=item.content)
            for item in invalid_lines[0:MAX_INVALID_COUNT]
        ])
        if (ignored_count := len(invalid_lines) - MAX_INVALID_COUNT, 0) > 0:
            content = ignored_template.format(content=content, ignored_count=ignored_count)
        dialog.show_warning(self.window, title_invalid, message_invalid_template.format(
            content=content,
            path=display_path
        ))

    def _show_generate_success_dialog(self, display_path: str):
        title_success = "生成 VCF 文件成功"
        message_success_template = "已导出文件到“{path}”。"
        dialog.show_info(self.window, title_success, message_success_template.format(path=display_path))

    def _clean_quotes(self):
        origin_text = self.window.get_text_content()
        new_text = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r'\1', origin_text, flags=re.S)
        self.window.set_text_content(new_text)
