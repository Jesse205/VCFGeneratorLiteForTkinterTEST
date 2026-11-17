"""构建截图场景并输出 PNG / WebP。"""

import time
from pathlib import Path
from tkinter import Menu, filedialog
from typing import override

from scripts.screenshot_support import apply_tk_fonts, capture_window, save_capture_as_webp
from vcf_generator_lite.ui.windows.invalid_items_dialog import InvalidItemsDialog
from vcf_generator_lite.ui.windows.main_window import VCFGeneratorLiteApp

MAIN_WINDOW_WIDTH_PT = 450
MAIN_WINDOW_HEIGHT_PT = 465
MAIN_WINDOW_MIN_SIZE_PT = 300
DIALOG_WIDTH_PT = 360
DIALOG_HEIGHT_PT = 320
DIALOG_MIN_SIZE_PT = 225
INVALID_ROW = 4
INVALID_PHONE_PLACEHOLDER = "x" * 11
DIALOG_TIMEOUT = 20.0


class ScreenshotApp(VCFGeneratorLiteApp):
    def __init__(self, *, platform: str, font_family: str):
        self._screenshot_platform = platform
        self._screenshot_font_family = font_family
        super().__init__()

    @override
    def _configure_ui_withdraw(self):
        apply_tk_fonts(self, self._screenshot_font_family)
        if self._screenshot_platform == "linux":
            from tkinter.ttk import Style

            Style(self).theme_use("clam")
        super()._configure_ui_withdraw()
        # 示例号码为中国号段；默认按语言territory选规则会让 en-US 下全部行无效。
        self.selected_phone_detectors_ids = set(self.phone_detectors_ids)
        self.menu_bar.set_phone_formats_selection(True, dict.fromkeys(self.phone_detectors_ids, True))
        self._strip_menu_underlines(self.menu_bar)
        self.set_screenshot_size(self, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT, MAIN_WINDOW_MIN_SIZE_PT)
        self._replace_invalid_row()

    @staticmethod
    def _strip_menu_underlines(menu: Menu):
        # X11 的 Tk 菜单常显助记符下划线，Windows 参考截图没有。
        for index in range(menu.index("end") + 1):
            entry_type = menu.type(index)
            if entry_type not in {"command", "cascade", "checkbutton", "radiobutton"}:
                continue
            menu.entryconfigure(index, underline=-1)
            if entry_type == "cascade":
                ScreenshotApp._strip_menu_underlines(menu.nametowidget(menu.entrycget(index, "menu")))

    def set_screenshot_size(
        self, window: VCFGeneratorLiteApp | InvalidItemsDialog, width_pt: int, height_pt: int, min_pt: int
    ):
        if self._screenshot_platform == "macos":
            # Aqua 的坐标单位是点（72dpi），Retina 下再经 wm_size_pt 换算会翻倍。
            window.wm_minsize(min_pt, min_pt)
            window.wm_size(width_pt, height_pt)
        else:
            window.wm_minsize_pt(min_pt, min_pt)
            window.wm_size_pt(width_pt, height_pt)

    def _replace_invalid_row(self):
        lines = self.layout.get_text_content().split("\n")
        name = lines[INVALID_ROW - 1].split("\t")[0]
        lines[INVALID_ROW - 1] = f"{name}\t{INVALID_PHONE_PLACEHOLDER}"
        self.layout.set_text_content("\n".join(lines))
        self.layout.content_text.edit_reset()
        self.layout.content_text.edit_modified(False)
        # 参考截图带插入光标；关闭闪烁避免截到隐藏相位。
        self.layout.content_text.configure(insertofftime=0)


def capture_language(
    *,
    output_dir: Path,
    platform: str,
    lang: str,
    font_family: str,
    scale: float,
    wait: float,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    app = ScreenshotApp(platform=platform, font_family=font_family)
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    save_path = desktop / app.save_vcf_file_name
    original_ask_saveasfilename = filedialog.asksaveasfilename

    def fake_ask_saveasfilename(**_kwargs: object) -> str:
        return str(save_path)

    filedialog.asksaveasfilename = fake_ask_saveasfilename
    # 生成线程会回调 Tk，必须跑真实 mainloop；update() 泵消息会让跨线程调用抛 RuntimeError。
    dialog_deadline = 0.0

    def capture_dialog(dialog: InvalidItemsDialog):
        _assert_size(dialog, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT)
        _capture(dialog, output_dir / f"invalid_lines_window.{lang}.png", platform)
        app.destroy()

    def wait_dialog():
        if time.monotonic() > dialog_deadline:
            raise SystemExit("等待无效号码弹窗超时。")
        for child in app.children.values():
            if isinstance(child, InvalidItemsDialog):
                app.set_screenshot_size(child, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT, DIALOG_MIN_SIZE_PT)
                child.attributes("-topmost", True)
                app.after(500, lambda: capture_dialog(child))
                return
        app.after(100, wait_dialog)

    def start_generate():
        nonlocal dialog_deadline
        _assert_scaling(app, platform, scale)
        _assert_size(app, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT)
        _capture(app, output_dir / f"main_window.{lang}.png", platform)
        dialog_deadline = time.monotonic() + DIALOG_TIMEOUT
        app.on_generate()
        app.after(100, wait_dialog)

    app.attributes("-topmost", True)
    app.after(int(wait * 1000), start_generate)
    try:
        app.mainloop()
    finally:
        filedialog.asksaveasfilename = original_ask_saveasfilename


def _capture(window: ScreenshotApp | InvalidItemsDialog, output: Path, platform: str) -> None:
    capture_window(window, output, platform)
    save_capture_as_webp(output, output.with_suffix(".webp"))
    print(f"已保存：{output}", flush=True)


def _assert_scaling(app: ScreenshotApp, platform: str, scale: float) -> None:
    actual = float(app.tk.call("tk", "scaling"))
    # X11 以 96dpi 为 1x，Aqua 以 72dpi 为 1x。
    expected = 96 / 72 * scale if platform == "linux" else scale
    print(f"[{platform}] tk scaling={actual:.3f}（期望 {expected:.3f}）", flush=True)
    if abs(actual - expected) > expected * 0.03:
        raise SystemExit(
            f"缩放未生效：tk scaling={actual:.3f}，期望 {expected:.3f}。"
            "Linux 请用 Xvfb -dpi 192 启动并合并 Xft.dpi；macOS 请确认显示器处于 HiDPI 2x 模式。"
        )


def _assert_size(window: ScreenshotApp | InvalidItemsDialog, width_pt: int, height_pt: int) -> None:
    expected_width = window.winfo_pixels(f"{width_pt}p")
    expected_height = window.winfo_pixels(f"{height_pt}p")
    if window.winfo_width() + 2 < expected_width or window.winfo_height() + 2 < expected_height:
        raise SystemExit(
            f"窗口被裁剪：{window.winfo_width()}x{window.winfo_height()}，"
            f"期望 {expected_width}x{expected_height}。请提高 runner 分辨率。"
        )
