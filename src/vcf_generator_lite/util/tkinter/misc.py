import re
from tkinter import Misc
from typing import Optional


class ScalingMiscExtension(Misc):
    _scale_factor: float = 1.0

    def __init__(self):
        self._scale_factor = self.scaling()

    def scaling(self, factor: Optional[float] = None):
        """
        设置或获取GUI缩放比例因子

        当传入factor参数时，设置当前缩放比例并应用新的缩放因子到Tkinter窗口。
        不传入参数时返回当前缩放比例因子。

        与 tk scaling ?-displayof window? ?number? 相同。
        """
        if factor is not None:
            self._scale_factor = factor
        return self.tk.call("tk", "scaling", factor)

    def get_scaled(self, value: int | float) -> int | float:
        if isinstance(value, int):
            return int(self._scale_factor * value)
        elif isinstance(value, float):
            return float(self._scale_factor * value)
        else:
            raise TypeError(f"{value} 必须为 int 或 float")

    def parse_dimen(self, value: str | int | float) -> float:
        if isinstance(value, int):
            return value
        match = re.match(r"([0-9.]+)([a-z]*)", value)
        value = float(match.group(1))
        unit = match.group(2)
        if unit == "p" or unit == "pt":
            return value * self._scale_factor
        else:
            return float(value)

    def scale_kw(self, **kw: int | float):
        new_kw = {key: self.get_scaled(value) for key, value in kw.items()}
        return new_kw

    def scale_args(self, *args: int | float):
        new_args = [self.get_scaled(value) for value in args]
        return new_args
