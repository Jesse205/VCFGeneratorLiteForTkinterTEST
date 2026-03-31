import logging
import platform
import re
import signal
import tkinter
import traceback
from pathlib import Path
from tkinter import Event, filedialog, messagebox
from types import FrameType
from typing import NamedTuple, TextIO

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


class Generation(NamedTuple):
    generator: VCFGeneratorTask
    file: Path
    file_io: TextIO


class MainController:
    def __init__(self, window: VCFGeneratorLiteApp):
        self.window = window
        self.is_exiting = False
        self.current_generation: Generation | None = None
        self.save_vcf_file_name: str = t("save_vcf_window.default_file_name")

        window.bind(EVENT_ABOUT, self.on_about)
        window.bind(EVENT_CLEAN_QUOTES, self.on_clean_quotes)
        window.bind(EVENT_GENERATE, self.on_generate)
        window.bind(EVENT_STOP, self.on_stop)
        window.bind(EVENT_GENERATE_OR_STOP, self.on_generate_or_stop)
        window.bind("<Control-Lock-G>", self.on_generate)
        window.bind("<Control-g>", self.on_generate)
        window.bind("<Return>", self.on_return)
        window.bind(EVENT_EXIT, self.on_exit)

        signal.signal(signal.SIGINT, self.signal_handler)

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
        self.stop()

    def on_generate_or_stop(self, event: Event):
        if self.current_generation:
            self.on_stop(event)
        else:
            self.on_generate(event)

    def pick_and_open_file(self) -> None | tuple[Path, TextIO]:
        file_path_str = filedialog.asksaveasfilename(
            title=t("save_vcf_window.title"),
            parent=self.window,
            initialfile=self.save_vcf_file_name,
            filetypes=[(t("save_vcf_window.label_type_vcf"), ".vcf")],
            defaultextension=".vcf",
        )
        if not file_path_str:
            return None
        generation_file = Path(file_path_str)
        self.save_vcf_file_name = generation_file.name
        try:
            file_io = generation_file.open("w", encoding="utf-8", newline="\r\n")
        except PermissionError:
            messagebox.showerror(
                title=t("save_vcf_permission_denied_message_box.title"),
                message=t("save_vcf_permission_denied_message_box.message"),
            )
            return None
        except OSError as e:
            messagebox.showerror(
                title=t("save_vcf_os_error_message_box.title"),
                message=t("save_vcf_os_error_message_box.message").format(reason=str(e)),
            )
            return None
        return generation_file, file_io

    def generate_file(self):
        if self.current_generation:
            return
        pick_result = self.pick_and_open_file()
        if not pick_result:
            return
        origin_text = self.window.get_text_content()
        file, file_io = pick_result

        generator = VCFGeneratorTask(
            input_text=origin_text,
            output_io=file_io,
            progress_listener=self.on_generation_update_progress,
            result_listener=self.on_generation_file_result,
        )
        self.current_generation = Generation(
            generator=generator,
            file=file,
            file_io=file_io,
        )

        self.window.set_progress(progress=0)
        self.window.set_progress_determinate(False)

        self.window.content_text.edit_modified(False)
        self.window.set_generating(True)
        self.window.update()

        generator.start()

    def on_generation_update_progress(self, progress: float, determinate: bool):
        if not self.current_generation:
            raise RuntimeError("Invoke callback without generating.")

        if self.current_generation.generator.is_stopping:
            return

        self.window.set_progress_determinate(determinate)
        if determinate:
            self.window.set_progress(progress)

    def on_generation_file_done(self, result: GenerateResult):
        generation = self.current_generation
        if not generation:
            raise RuntimeError("Invoke callback without generating.")

        self.current_generation = None

        self.window.set_generating(False)
        self.window.update()

        if not self.is_exiting:
            self._show_generation_done_dialog(
                display_path=str(generation.file),
                generate_result=result,
            )
        else:
            self.window.event_generate(EVENT_EXIT)

    def on_generation_file_result(self, result: GenerateResult):
        if not self.current_generation:
            raise RuntimeError("Invoke callback without generating.")
        self.current_generation.file_io.close()

        self.window.after_idle(self.on_generation_file_done, result)

    def signal_handler(self, sig_num: int, _frame: FrameType | None):
        if sig_num == signal.SIGINT:
            self.window.event_generate(EVENT_EXIT)

    def stop(self):
        generation = self.current_generation
        if generation is None or generation.generator.is_stopping or not generation.generator.is_alive():
            return

        self.window.set_generating("stopping")
        generation.generator.stop()

    def on_exit(self, _: Event):
        self.is_exiting = True
        if self.current_generation:
            self.stop()
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

    def _show_generation_done_dialog(self, display_path: str, generate_result: GenerateResult):
        if generate_result.exception:
            self._show_generation_error_dialog(generate_result.exception)
        elif len(generate_result.invalid_items) > 0:
            self._show_generation_invalid_dialog(display_path, generate_result.invalid_items)
        else:
            self._show_generation_success_dialog(display_path, generate_result)

    def _show_generation_error_dialog(self, exception: BaseException):
        messagebox.showerror(
            parent=self.window,
            title=t("vcf_generate_error_message_box.title"),
            message=t("vcf_generate_error_message_box.message").format(
                exception="\n".join(traceback.format_exception(exception)),
            ),
        )

    def _show_generation_invalid_dialog(self, display_path: str, invalid_items: list[InvalidItem]):
        _, invalid_lines_controller = create_invalid_items_dialog(self.window, display_path, invalid_items)
        invalid_lines_controller.set_line_enter_listener(self.__on_select_invalid_line)

    def _show_generation_success_dialog(self, display_path: str, generate_result: GenerateResult):
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
