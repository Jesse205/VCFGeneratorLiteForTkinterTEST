"""构建截图场景并输出 PNG / WebP（亮/暗窗口后背景 + 透明）。"""

import importlib
import subprocess
import time
from contextlib import suppress
from functools import partial
from pathlib import Path
from tkinter import Menu, TclError, filedialog
from typing import override

from scripts.screenshot_support import (
    apply_tk_fonts,
    composite_over,
    derive_transparent,
    grab_window,
    require_executable,
    save_image,
)
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
BACKGROUNDS = (("light", "#ffffff"), ("dark", "#000000"))


class ScreenshotApp(VCFGeneratorLiteApp):
    def __init__(self, *, platform: str, font_family: str, ttk_theme: str, theme_dirs: list[str]):
        self._screenshot_platform = platform
        self._screenshot_font_family = font_family
        self._screenshot_ttk_theme = ttk_theme
        self._screenshot_theme_dirs = theme_dirs
        super().__init__()

    @override
    def _configure_ui_withdraw(self):
        apply_tk_fonts(self, self._screenshot_font_family)
        if self._screenshot_platform == "linux":
            self._load_external_themes()
            self._use_ttk_theme()
        super()._configure_ui_withdraw()
        if self._screenshot_platform == "linux":
            self._patch_text_style()
        # 示例号码为中国号段；默认按语言 territory 选规则会让 en-US 下全部行无效。
        self.selected_phone_detectors_ids = set(self.phone_detectors_ids)
        self.menu_bar.set_phone_formats_selection(True, dict.fromkeys(self.phone_detectors_ids, True))
        _strip_menu_underlines(self.menu_bar)
        self.set_screenshot_size(self, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT, MAIN_WINDOW_MIN_SIZE_PT)
        self._replace_invalid_row()

    def _load_external_themes(self):
        # tksvg 无 cp312 wheel、仅源码构建，不作硬依赖；svg 主题需要它。
        with suppress(ImportError):
            tksvg = importlib.import_module("tksvg")
            with suppress(TclError):
                tksvg.load(self)
        for directory in self._screenshot_theme_dirs:
            base = Path(directory)
            if not base.is_dir():
                raise SystemExit(f"主题目录不存在：{base}")
            for candidate in [base, *(p for p in sorted(base.iterdir()) if p.is_dir())]:
                pkg_index = candidate / "pkgIndex.tcl"
                if not pkg_index.is_file():
                    continue
                self.tk.call("lappend", "auto_path", str(candidate))
                # pkgIndex 依赖包加载器注入的 dir 变量；动态注册（foreach）也需 source 后才可见。
                with suppress(TclError):
                    self.tk.call("set", "dir", str(candidate))
                    self.tk.call("source", str(pkg_index))
        for name in self.tk.call("package", "names"):
            if str(name).startswith("ttk::theme::"):
                with suppress(TclError):
                    self.tk.call("package", "require", name)

    def _use_ttk_theme(self):
        from tkinter import font
        from tkinter.ttk import Style

        style = Style(self)
        names = style.theme_names()
        target = next((n for n in names if n.lower() == self._screenshot_ttk_theme.lower()), None)
        if target is None:
            raise SystemExit(f"ttk 主题 {self._screenshot_ttk_theme!r} 不可用；当前：{names}")
        style.theme_use(target)
        # 部分主题用字体 spec（如 "Helvetica 10"）而非命名字体；app 的 lookup_font 按命名取，
        # 故把 spec 注册为命名字体，族统一为开源字体。
        existing = set(font.names())
        # 命名字体随 Font 对象析构而删除，必须持有引用。
        self._spec_fonts = []
        for element in (".", "Treeview", "TButton", "TEntry", "TLabel", "Heading"):
            spec = style.lookup(element, "font")
            if not spec or spec in existing:
                continue
            parts = str(spec).split()
            size = int(parts[-1]) if parts and parts[-1].lstrip("-").isdigit() else 10
            weight = "bold" if "bold" in parts else "normal"
            self._spec_fonts.append(
                font.Font(root=self, name=str(spec), family=self._screenshot_font_family, size=size, weight=weight)
            )
            existing.add(str(spec))

    def _patch_text_style(self):
        # ttk-text 的核心 Text 不随 ttk 主题；按 TEntry 取值补齐，使观感与正常 entry 一致。
        from tkinter.ttk import Style

        style = Style(self)
        text = self.layout.content_text
        background = style.lookup("TEntry", "fieldbackground") or style.lookup("TEntry", "background") or "#ffffff"
        foreground = style.lookup("TEntry", "foreground") or "#000000"
        select_background = style.lookup("TEntry", "selectbackground") or background
        select_foreground = style.lookup("TEntry", "selectforeground") or foreground
        border_color = style.lookup("TEntry", "bordercolor") or background
        focus_color = style.lookup("TEntry", "bordercolor", state=["focus"]) or border_color
        text.configure(
            background=background,
            foreground=foreground,
            selectbackground=select_background,
            selectforeground=select_foreground,
            insertbackground=foreground,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=border_color,
            highlightcolor=focus_color,
        )
        self.layout.line_numbers.update_style()

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


def _strip_menu_underlines(menu: Menu):
    # X11 的 Tk 菜单常显助记符下划线，Windows 参考截图没有。
    end = menu.index("end")
    if end is None:
        return
    for index in range(int(end) + 1):
        entry_type = menu.type(index)
        if entry_type not in {"command", "cascade", "checkbutton", "radiobutton"}:
            continue
        menu.entryconfigure(index, underline=-1)
        if entry_type == "cascade":
            _strip_menu_underlines(menu.nametowidget(menu.entrycget(index, "menu")))


def _settle(window: VCFGeneratorLiteApp | InvalidItemsDialog):
    window.update()
    time.sleep(0.2)
    window.update()


def _capture_scene(
    window: VCFGeneratorLiteApp | InvalidItemsDialog,
    scene: str,
    output_dir: Path,
    lang: str,
    platform: str,
):
    if platform == "linux":
        grabs = {}
        xsetroot = require_executable("xsetroot")
        for background, color in BACKGROUNDS:
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [xsetroot, "-solid", color],
                check=True,
            )
            _settle(window)
            grabs[background] = grab_window(window, platform)
        images = {**grabs, "transparent": derive_transparent(grabs["light"], grabs["dark"])}
    else:
        transparent = grab_window(window, platform)
        images = {
            "transparent": transparent,
            **{background: composite_over(transparent, color) for background, color in BACKGROUNDS},
        }
    for background, image in images.items():
        save_image(image, output_dir / f"{scene}.{lang}.{background}.png")


def capture_language(
    *,
    output_dir: Path,
    platform: str,
    lang: str,
    font_family: str,
    ttk_theme: str,
    theme_dirs: list[str],
    scale: float,
    wait: float,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    app = ScreenshotApp(platform=platform, font_family=font_family, ttk_theme=ttk_theme, theme_dirs=theme_dirs)
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
        _capture_scene(dialog, "invalid_lines_window", output_dir, lang, platform)
        app.destroy()

    def wait_dialog():
        if time.monotonic() > dialog_deadline:
            raise SystemExit("等待无效号码弹窗超时。")
        for child in app.children.values():
            if isinstance(child, InvalidItemsDialog):
                app.set_screenshot_size(child, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT, DIALOG_MIN_SIZE_PT)
                child.attributes("-topmost", True)
                child.focus_force()
                app.after(500, partial(capture_dialog, child))
                return
        app.after(100, wait_dialog)

    def capture_main_and_generate():
        nonlocal dialog_deadline
        _assert_scaling(app, platform, scale)
        _assert_size(app, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT)
        _capture_scene(app, "main_window", output_dir, lang, platform)
        dialog_deadline = time.monotonic() + DIALOG_TIMEOUT
        app.on_generate()
        app.after(100, wait_dialog)

    def start_generate():
        # WM 焦点策略不一，显式索取焦点保证插入光标可见。
        app.focus_force()
        app.layout.content_text.focus_set()
        app.after(300, capture_main_and_generate)

    app.attributes("-topmost", True)
    app.after(int(wait * 1000), start_generate)
    try:
        app.mainloop()
    finally:
        filedialog.asksaveasfilename = original_ask_saveasfilename


def _assert_scaling(app: ScreenshotApp, platform: str, scale: float) -> None:
    actual = float(app.tk.call("tk", "scaling"))
    # X11 以 96dpi 为 1x，Aqua 以 72dpi 为 1x。
    expected = 96 / 72 * scale if platform == "linux" else scale
    print(f"[{platform}] tk scaling={actual:.3f}（期望 {expected:.3f}）", flush=True)
    if abs(actual - expected) > expected * 0.03:
        raise SystemExit(
            f"缩放未生效：tk scaling={actual:.3f}，期望 {expected:.3f}。"
            "Linux 请检查 Xvfb -dpi 与 Xft.dpi；macOS 请确认显示器处于 HiDPI 2x 模式。"
        )


def _assert_size(window: ScreenshotApp | InvalidItemsDialog, width_pt: int, height_pt: int) -> None:
    expected_width = window.winfo_pixels(f"{width_pt}p")
    expected_height = window.winfo_pixels(f"{height_pt}p")
    if window.winfo_width() + 2 < expected_width or window.winfo_height() + 2 < expected_height:
        raise SystemExit(
            f"窗口被裁剪：{window.winfo_width()}x{window.winfo_height()}，"
            f"期望 {expected_width}x{expected_height}。请提高 runner 分辨率。"
        )
