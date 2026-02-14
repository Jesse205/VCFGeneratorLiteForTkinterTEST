import logging
import os.path
import re
import traceback
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import Event, filedialog, messagebox
from typing import IO

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT
from vcf_generator_lite.core.vcf_generator import GenerateResult, InvalidLine, VCFGeneratorTask
from vcf_generator_lite.utils.locales import t
from vcf_generator_lite.utils.tkinter.text import search_line, select_text
from vcf_generator_lite.windows.base.constants import EVENT_EXIT
from vcf_generator_lite.windows.invalid_lines import create_invalid_lines_window
from vcf_generator_lite.windows.main.constants import EVENT_ABOUT, EVENT_CLEAN_QUOTES, EVENT_GENERATE
from vcf_generator_lite.windows.main.window import VCFGeneratorLiteApp

logger = logging.getLogger(__name__)


class MainController:
    def __init__(self, window: VCFGeneratorLiteApp):
        self.window = window
        self.is_generating: bool = False
        self.generate_file_name: str = "phones.vcf"

        window.bind(EVENT_ABOUT, self.on_about)
        window.bind(EVENT_CLEAN_QUOTES, self.on_clean_quotes)
        window.bind(EVENT_GENERATE, self.on_generate)
        window.bind("<Control-Lock-G>", self.on_generate)
        window.bind("<Control-g>", self.on_generate)
        window.bind("<Return>", self.on_return)
        window.bind(EVENT_EXIT, self.on_exit)

    def on_about(self, _: Event):
        self._show_about_message_box()

    def on_clean_quotes(self, _: Event):
        self._clean_quotes()

    def on_return(self, event: Event):
        if event.widget in self.window.content_text.frame.winfo_children():
            return
        self.window.generate_button.invoke()

    def on_generate(self, _: Event):
        self.generate_file()

    def pick_output_file(self) -> IO[str] | None:
        file_io: IO[str] | None = None
        try:
            file_io = filedialog.asksaveasfile(
                title=t("save_vcf_window.title"),
                parent=self.window,
                initialfile=self.generate_file_name,
                filetypes=[(t("save_vcf_window.label_type_vcf"), ".vcf")],
                defaultextension=".vcf",
            )
        except PermissionError:
            messagebox.showerror(
                title=t("save_vcf_permission_denied_message_box.title"),
                message=t("save_vcf_permission_denied_message_box.message"),
            )
        except OSError as e:
            messagebox.showerror(
                title=t("save_vcf_os_error_message_box.title"),
                message=t("save_vcf_os_error_message_box.message").format(reason=str(e)),
            )
        return file_io

    def generate_file(self):
        if self.is_generating:
            return

        file_io = self.pick_output_file()
        if file_io is None:
            return

        origin_text = self.window.get_text_content()
        self.generate_file_name = os.path.basename(file_io.name)
        self.is_generating = True

        self.window.set_progress(progress=0)
        self.window.set_progress_determinate(False)

        self.window.content_text.edit_modified(False)
        self.window.set_generating(True)
        self.window.update()

        generator = VCFGeneratorTask(
            executor=ThreadPoolExecutor(max_workers=1),
            progress_listener=self.on_generate_file_update_progress,
            input_text=origin_text,
            output_io=file_io,
        )
        generate_future = generator.start()
        generate_future.add_done_callback(
            lambda future: self.window.after_idle(self.on_generate_file_done, future, file_io)
        )
        generate_future.add_done_callback(lambda _: self.window.after_idle(callable, file_io))

    def on_generate_file_update_progress(self, progress: float, determinate: bool):
        self.window.set_progress_determinate(determinate)
        if determinate:
            self.window.set_progress(progress)

    def on_generate_file_done(
        self,
        future: Future[GenerateResult],
        file_io: IO[str],
    ):
        try:
            file_io.close()
        except BaseException as e:
            logger.error("Closing file failed: {}.", e)
        self.is_generating = False

        self.window.set_generating(False)
        self.window.update()

        result = future.result()
        self._show_generate_done_dialog(file_io.name, result)

    def on_exit(self, _: Event):
        if self.is_generating:
            messagebox.showwarning(
                parent=self.window,
                title=t("vcf_generating_exit_message_box.title"),
                message=t("vcf_generating_exit_message_box.message"),
            )
        else:
            self.window.destroy()

    def _show_about_message_box(self):
        messagebox.showinfo(
            parent=self.window,
            title=t("about_message_box.title"),
            message=t("about_message_box.message").format(
                version=__version__,
            ),
            detail=t("about_message_box.detail").format(
                copyright=APP_COPYRIGHT,
            ),
        )

    def _show_generate_done_dialog(self, display_path: str, generate_result: GenerateResult):
        if generate_result.exception:
            self._show_generate_error_dialog(generate_result.exception)
        elif len(generate_result.invalid_lines) > 0:
            self._show_generate_invalid_dialog(display_path, generate_result.invalid_lines)
        else:
            self._show_generate_success_dialog(display_path, generate_result)

    def _show_generate_error_dialog(self, exception: BaseException):
        messagebox.showerror(
            parent=self.window,
            title=t("vcf_generate_error_message_box.title"),
            message=t("vcf_generate_error_message_box.message").format(
                content="\n".join(traceback.format_exception(exception)),
            ),
        )

    def _show_generate_invalid_dialog(self, display_path: str, invalid_lines: list[InvalidLine]):
        _, invalid_lines_controller = create_invalid_lines_window(self.window, display_path, invalid_lines)
        invalid_lines_controller.set_line_enter_listener(self.__on_select_invalid_line)

    def _show_generate_success_dialog(self, display_path: str, generate_result: GenerateResult):
        messagebox.showinfo(
            parent=self.window,
            title=t("vcf_generate_success_message_box.title"),
            message=t("vcf_generate_success_message_box.message").format(path=display_path),
            detail=t("vcf_generate_success_message_box.detail").format(
                total=generate_result.total,
                time=round(generate_result.time_elapsed, 3),
            ),
        )

    def __on_select_invalid_line(self, line: int, data: str):
        actual_line: int | None = None
        if self.window.content_text.get(f"{line}.0", f"{line}.end") == data:
            actual_line = line
        else:
            search_row = search_line(self.window.content_text, data, line)
            actual_line = int(search_row) if search_row else None

        if actual_line:
            self.window.deiconify()
            self.window.lift()
            self.window.content_text.focus()
            select_text(self.window.content_text, f"{actual_line}.0", f"{actual_line}.end")

    def _clean_quotes(self):
        origin_text = self.window.get_text_content()
        new_text = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r"\1", origin_text, flags=re.S)
        self.window.set_text_content(new_text)
