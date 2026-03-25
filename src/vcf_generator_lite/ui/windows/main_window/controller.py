import logging
import platform
import re
import tkinter
import traceback
from pathlib import Path
from tkinter import Event, filedialog, messagebox

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT
from vcf_generator_lite.core.vcf_generator import GenerateResult, InvalidItem, VCFGeneratorTask
from vcf_generator_lite.ui.windows.base_window.constants import EVENT_EXIT
from vcf_generator_lite.ui.windows.invalid_items_dialog import create_invalid_items_dialog
from vcf_generator_lite.ui.windows.main_window.constants import (
    EVENT_ABOUT,
    EVENT_CLEAN_QUOTES,
    EVENT_GENERATE,
    EVENT_GENERATE_OR_STOP,
    EVENT_STOP,
)
from vcf_generator_lite.ui.windows.main_window.window import VCFGeneratorLiteApp
from vcf_generator_lite.utils.locales import t
from vcf_generator_lite.utils.tkinter.text import search_line, select_text

logger = logging.getLogger(__name__)


class MainController:
    def __init__(self, window: VCFGeneratorLiteApp):
        self.window = window
        self.is_generating: bool = False
        self.generate_file_name: str = "phones.vcf"
        self.generator: VCFGeneratorTask | None = None

        window.bind(EVENT_ABOUT, self.on_about)
        window.bind(EVENT_CLEAN_QUOTES, self.on_clean_quotes)
        window.bind(EVENT_GENERATE, self.on_generate)
        window.bind(EVENT_STOP, self.on_stop)
        window.bind(EVENT_GENERATE_OR_STOP, self.on_generate_or_stop)
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
        self.window.generate_or_stop_button.invoke()

    def on_generate(self, _: Event):
        self.generate_file()

    def on_stop(self, _: Event):
        if self.generator is None or self.generator.is_stopping:
            return
        self.window.set_generating("stopping")
        self.generator.stop()

    def on_generate_or_stop(self, event: Event):
        if self.is_generating:
            self.on_stop(event)
        else:
            self.on_generate(event)

    def generate_file(self):
        if self.is_generating:
            return

        file_path_str = filedialog.asksaveasfilename(
            title=t("save_vcf_window.title"),
            parent=self.window,
            initialfile=self.generate_file_name,
            filetypes=[(t("save_vcf_window.label_type_vcf"), ".vcf")],
            defaultextension=".vcf",
        )
        if not file_path_str:
            return
        file_path = Path(file_path_str)
        try:
            file_io = file_path.open("w", encoding="utf-8", newline="\r\n")
        except PermissionError:
            messagebox.showerror(
                title=t("save_vcf_permission_denied_message_box.title"),
                message=t("save_vcf_permission_denied_message_box.message"),
            )
            return
        except OSError as e:
            messagebox.showerror(
                title=t("save_vcf_os_error_message_box.title"),
                message=t("save_vcf_os_error_message_box.message").format(reason=str(e)),
            )
            return

        origin_text = self.window.get_text_content()
        self.generate_file_name = file_path.name
        self.is_generating = True

        self.window.set_progress(progress=0)
        self.window.set_progress_determinate(False)

        self.window.content_text.edit_modified(False)
        self.window.set_generating(True)
        self.window.update()

        def on_update_progress(progress: float, determinate: bool):
            if self.generator and self.generator.is_stopping:
                return
            self.window.set_progress_determinate(determinate)
            if determinate:
                self.window.set_progress(progress)

        def on_generate_file_done(result: GenerateResult):
            self.is_generating = False

            self.window.set_generating(False)
            self.window.update()

            self._show_generate_done_dialog(str(file_path), result)

        def on_generate_file_result(result: GenerateResult):
            file_io.close()

            self.generator = None
            self.window.after_idle(on_generate_file_done, result)

        self.generator = VCFGeneratorTask(
            input_text=origin_text,
            output_io=file_io,
            progress_listener=on_update_progress,
            result_listener=on_generate_file_result,
        )
        self.generator.start()

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
                python_info=f"{platform.python_implementation()} v{platform.python_version()}",
                tcl_info=f"v{tkinter.TclVersion}",
                tk_info=f"v{tkinter.TkVersion}",
            ),
        )

    def _show_generate_done_dialog(self, display_path: str, generate_result: GenerateResult):
        if generate_result.exception:
            self._show_generate_error_dialog(generate_result.exception)
        elif len(generate_result.invalid_items) > 0:
            self._show_generate_invalid_dialog(display_path, generate_result.invalid_items)
        else:
            self._show_generate_success_dialog(display_path, generate_result)

    def _show_generate_error_dialog(self, exception: BaseException):
        messagebox.showerror(
            parent=self.window,
            title=t("vcf_generate_error_message_box.title"),
            message=t("vcf_generate_error_message_box.message").format(
                exception="\n".join(traceback.format_exception(exception)),
            ),
        )

    def _show_generate_invalid_dialog(self, display_path: str, invalid_lines: list[InvalidItem]):
        _, invalid_lines_controller = create_invalid_items_dialog(self.window, display_path, invalid_lines)
        invalid_lines_controller.set_line_enter_listener(self.__on_select_invalid_line)

    def _show_generate_success_dialog(self, display_path: str, generate_result: GenerateResult):
        messagebox.showinfo(
            parent=self.window,
            title=t("vcf_generate_success_message_box.title"),
            message=t("vcf_generate_success_message_box.message").format(path=display_path),
            detail=t("vcf_generate_success_message_box.detail").format(
                count=generate_result.saved_count,
                time=generate_result.time_elapsed,
            ),
        )

    def __on_select_invalid_line(self, line: int, data: str):
        actual_line: int | None
        if self.window.content_text.get(f"{line}.0", f"{line}.end") == data:
            actual_line = line
        else:
            search_row = search_line(self.window.content_text, data, line, strip=True)
            actual_line = int(search_row) if search_row else None

        if actual_line:
            self.window.deiconify()
            self.window.lift()
            self.window.content_text.focus()
            select_text(self.window.content_text, f"{actual_line}.0", f"{actual_line}.end")

    def _clean_quotes(self):
        origin_text = self.window.get_text_content()
        new_text = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r"\1", origin_text, flags=re.DOTALL)
        self.window.set_text_content(new_text)
