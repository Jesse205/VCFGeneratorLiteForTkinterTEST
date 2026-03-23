import logging
from abc import ABC
from tkinter import Event, PhotoImage, Tk, Toplevel, Wm
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.ui.themes import create_theme_patch
from vcf_generator_lite.ui.themes.abs import ThemePatch
from vcf_generator_lite.ui.windows.base_window.constants import EVENT_EXIT
from vcf_generator_lite.utils import resources
from vcf_generator_lite.utils.tkinter.window import (
    CenterWindowExtension,
    GeometryWindowExtension,
    WindowExtension,
    withdraw_cm,
)

__all__ = ["EnhancedTk", "EnhancedToplevel", "EnhancedDialog"]
_logger = logging.getLogger(__name__)


class AppWindowExtension(
    GeometryWindowExtension,
    CenterWindowExtension,
    WindowExtension,
    ABC,
):
    """
    应用程序窗口扩展基类，集成多个窗口功能扩展

    特性：
    - 继承 GeometryWindowExtension: 提供基于物理/虚拟像素的窗口尺寸控制
    - 继承 ScalingWindowExtension: 支持高 DPI 屏幕的自适应缩放
    - 继承 CenterWindowExtension: 实现窗口居中显示功能
    - 继承 WindowExtension: 基础窗口功能扩展
    """

    def __init__(self):
        super().__init__()
        with withdraw_cm(self):
            self._configure_ui_withdraw()
            self.update_idletasks()  # 在 deiconify 前调用可以一定程度上防止首次启动时窗口闪烁
        self._configure_ui()

    def _configure_ui_withdraw(self):
        # 为了在系统主题切换时正确更新背景而浪费系统资源没必要，并且还要其他地方不会更新配色，用户只能重启解决。
        # self.root_frame = Frame(self)
        # self.root_frame.place(relwidth=1, relheight=1)
        self.__apply_default_events()

    def _configure_ui(self):
        if self.master is not None:
            self.center_reference_master()
        elif self._windowingsystem == "win32":
            # 居中于屏幕功能在 Linux 端的多屏下表现得不是很好，因此遵循默认设定。
            self.center_reference_screen()

    def __apply_default_events(self):
        self.protocol("WM_DELETE_WINDOW", lambda: self.event_generate(EVENT_EXIT))
        self.bind(EVENT_EXIT, lambda _: self.destroy())


class EnhancedTk(Tk, AppWindowExtension, ABC):
    def __init__(self, **kw):
        super().__init__(baseName="vcf_generator_lite", **kw)
        self.theme_name: str | None = None
        self.theme_patch: ThemePatch | None = None
        AppWindowExtension.__init__(self)

    @override
    def _configure_ui_withdraw(self):
        self.apply_theme_patch()
        super()._configure_ui_withdraw()
        self.__apply_default_icon()
        self.bind("<<ThemeChanged>>", self.__on_theme_changed, "+")

    def __apply_default_icon(self):
        self.iconphoto(True, PhotoImage(master=self, data=resources.read_binary("images/icon-48.png")))

    def apply_theme_patch(self):
        theme_name = Style(self).theme_use()
        if self.theme_name == theme_name:
            return
        self.theme_name = theme_name
        self.theme_patch = create_theme_patch(self, theme_name)

    def __on_theme_changed(self, event: Event):
        if event.widget != self:
            return
        self.apply_theme_patch()


class EnhancedToplevel(Toplevel, AppWindowExtension, ABC):
    def __init__(self, master: Tk | Toplevel, **kw):
        super().__init__(master, **kw)
        AppWindowExtension.__init__(self)

    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()


class EnhancedDialog(EnhancedToplevel, ABC):
    @override
    def _configure_ui_withdraw(self):
        super()._configure_ui_withdraw()
        self.bind("<Escape>", lambda _: self.event_generate(EVENT_EXIT))

        if isinstance(self.master, Wm):
            self.transient(self.master)
            self.resizable(False, False)
