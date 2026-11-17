"""构建截图场景并输出 PNG / WebP。"""

import time
from pathlib import Path
from tkinter import filedialog
from typing import override

from scripts.screenshot_support import apply_tk_fonts, capture_window, pump, save_capture_as_webp
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
        self.set_screenshot_size(self, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT, MAIN_WINDOW_MIN_SIZE_PT)
        self._replace_invalid_row()

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
        self.layout.set_text_content("\n".join(lines) + "\n")
        self.layout.content_text.edit_reset()
        self.layout.content_text.edit_modified(False)


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
    try:
        app.attributes("-topmost", True)
        pump(app, wait)
        _assert_scaling(app, platform, scale)
        _assert_size(app, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT)
        _capture(app, output_dir / f"main_window.{lang}.png", platform)

        app.on_generate()
        dialog = _wait_for_dialog(app)
        app.set_screenshot_size(dialog, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT, DIALOG_MIN_SIZE_PT)
        dialog.attributes("-topmost", True)
        pump(dialog, 0.5)
        _assert_size(dialog, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT)
        _capture(dialog, output_dir / f"invalid_lines_window.{lang}.png", platform)
    finally:
        filedialog.asksaveasfilename = original_ask_saveasfilename
        app.destroy()


def _wait_for_dialog(app: ScreenshotApp) -> InvalidItemsDialog:
    deadline = time.monotonic() + DIALOG_TIMEOUT
    while time.monotonic() < deadline:
        pump(app, 0.1)
        for child in app.children.values():
            if isinstance(child, InvalidItemsDialog):
                return child
    raise SystemExit("等待无效号码弹窗超时。")


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
