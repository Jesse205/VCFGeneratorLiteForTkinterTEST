import logging
from abc import ABC, abstractmethod
from tkinter import *
from typing import override

from vcf_generator_lite.theme import get_platform_theme
from vcf_generator_lite.util.display import get_scale_factor
from vcf_generator_lite.util.resource import get_asset_data
from vcf_generator_lite.util.tkinter.window import CenterWindowExtension, GeometryWindowExtension, \
    ScalingWindowExtension, WindowExtension, \
    withdraw_cm
from vcf_generator_lite.window.base.constants import EVENT_EXIT

__all__ = ["ExtendedTk", "ExtendedToplevel", "ExtendedDialog"]

logger = logging.getLogger(__name__)


class AppWindowExtension(GeometryWindowExtension, ScalingWindowExtension, CenterWindowExtension, WindowExtension, ABC):

    def __init__(self):
        super().__init__()
        self.__apply_default_scaling()
        self.__apply_default_icon()
        self.__apply_default_events()
        self.on_init_window()

    @abstractmethod
    def on_init_window(self):
        pass

    def __apply_default_scaling(self):
        self.scaling(get_scale_factor(self))

    def __apply_default_icon(self):
        logger.debug(f"窗口 {self.winfo_name()} 默认图标为 icon-48.png")
        self.iconphoto(True, PhotoImage(master=self, data=get_asset_data("images/icon-48.png")))

    def __apply_default_events(self):
        self.protocol("WM_DELETE_WINDOW", lambda: self.event_generate(EVENT_EXIT))
        self.bind(EVENT_EXIT, lambda _: self.destroy())


class ExtendedTk(Tk, AppWindowExtension, ABC):
    def __init__(self, **kw):
        super().__init__(**kw)
        with withdraw_cm(self):
            get_platform_theme().apply_theme(self)
            AppWindowExtension.__init__(self)
            self.center()


class ExtendedToplevel(Toplevel, AppWindowExtension, ABC):
    def __init__(self, master: Tk | Toplevel, **kw):
        super().__init__(master, **kw)
        with withdraw_cm(self):
            AppWindowExtension.__init__(self)
            if isinstance(self.master, Tk) or isinstance(self.master, Toplevel):
                self.center(self.master)


class ExtendedDialog(ExtendedToplevel, ABC):
    @abstractmethod
    @override
    def on_init_window(self):
        self.bind("<Escape>", lambda _: self.event_generate(EVENT_EXIT))

        if isinstance(self.master, Wm):
            self.transient(self.master)
            self.resizable(False, False)
