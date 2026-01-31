import logging
import os.path
import re
import traceback
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import Event, filedialog, messagebox

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT
from vcf_generator_lite.core.vcf_generator import GenerateResult, InvalidLine, VCFGeneratorTask
from vcf_generator_lite.utils.locales import t
from vcf_generator_lite.utils.tkinter.busy import tk_busy_forget, tk_buy_hold
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
        if event.widget is self.window.content_text:
            return
        self.window.generate_button.invoke()

    def on_generate(self, _: Event):
        if self.is_generating:
            return
        text_content = self.window.get_text_content()
        file_io = None
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
            return
        except OSError as e:
            messagebox.showerror(
                title=t("save_vcf_os_error_message_box.title"),
                message=t("save_vcf_os_error_message_box.message").format(reason=str(e)),
            )
            return

        if file_io is None:
            return
        self.generate_file_name = os.path.basename(file_io.name)
        self.is_generating = True
        self.window.show_progress()
        self.window.set_progress(progress=0)
        self.window.set_progress_determinate(False)
        self.window.set_generate_enabled(False)
        tk_buy_hold(self.window.generate_button)
        self.window.update()

        def done(future: Future[GenerateResult]):
            self.is_generating = False
            try:
                file_io.close()
            except BaseException as e:
                logger.error("Closing file failed: {}", e)
            self.window.hide_progress()
            self.window.update()
            self._show_generate_done_dialog(file_io.name, future.result())
            self.window.set_generate_enabled(True)
            tk_busy_forget(self.window.generate_button)
            self.window.update()

        def on_update_progress(progress: float, determinate: bool):
            self.window.set_progress_determinate(determinate)
            if determinate:
                self.window.set_progress(progress)

        executor = ThreadPoolExecutor(max_workers=1)
        generator = VCFGeneratorTask(
            executor=executor,
            progress_listener=on_update_progress,
            input_text=text_content,
            output_io=file_io,
        )
        generate_future = generator.start()
        generate_future.add_done_callback(lambda future: self.window.after_idle(done, future))
        executor.shutdown(wait=False)

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
            self._show_generate_success_dialog(display_path)

    def _show_generate_error_dialog(self, exception: BaseException):
        messagebox.showerror(
            parent=self.window,
            title=t("vcf_generate_error_message_box.title"),
            message=t("vcf_generate_error_message_box.message").format(
                content="\n".join(traceback.format_exception(exception)),
            ),
        )

    def _show_generate_invalid_dialog(self, display_path: str, invalid_lines: list[InvalidLine]):
        create_invalid_lines_window(self.window, display_path, invalid_lines)

    def _show_generate_success_dialog(self, display_path: str):
        messagebox.showinfo(
            parent=self.window,
            title=t("vcf_generate_success_message_box.title"),
            message=t("vcf_generate_success_message_box.message").format(path=display_path),
        )

    def _clean_quotes(self):
        origin_text = self.window.get_text_content()
        new_text = re.sub(r'"\s*(([^"\s][^"]*[^"\s])|[^"\s]?)\s*"', r"\1", origin_text, flags=re.S)
        self.window.set_text_content(new_text)
