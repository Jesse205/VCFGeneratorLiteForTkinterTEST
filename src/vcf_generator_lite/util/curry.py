import threading
from collections.abc import Callable
from tkinter import Misc
from typing import Any, Optional


class TkDebounceWrapper[**P, T]:
    _pending_args: Optional[tuple[Any]] = None
    _pending_kwargs: Optional[dict[str, Any]] = None
    _after_id = None

    def __init__(self, widget: Misc, func: Callable[P, T], ms: int, *, leading: bool = False, trailing: bool = True):
        self._widget = widget
        self._func = func
        self._ms = ms
        self._leading = leading
        self._trailing = trailing
        self._after_id = None
        self.lock = threading.RLock()

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        with self.lock:
            self._cancel_timer()
            self._update_pending_args(args, kwargs)
            if self._leading and not self.is_pending:
                self._invoke_idle()
            self._after_id = self._widget.after(self._ms, self._on_time_end)

    def _invoke(self):
        with self.lock:
            assert self._pending_args is not None and self._pending_kwargs is not None, "pending args and kwargs must not be None"
            self._func(*self._pending_args, **self._pending_kwargs)

    def _invoke_idle(self):
        self._widget.after_idle(self._invoke)

    def _on_time_end(self):
        with self.lock:
            self._after_id = None
            if self._trailing:
                self._invoke()
            self._update_pending_args(None, None)

    def _cancel_timer(self):
        with self.lock:
            if self._after_id is not None:
                self._widget.after_cancel(self._after_id)
                self._after_id = None

    def _update_pending_args(self, args: Optional[tuple[Any]], kwargs: Optional[dict[str, Any]]):
        with self.lock:
            self._pending_args = args
            self._pending_kwargs = kwargs

    @property
    def is_pending(self) -> bool:
        return self._after_id is not None

    def cancel(self):
        with self.lock:
            self._cancel_timer()
            self._update_pending_args(None, None)

    def flush(self):
        with self.lock:
            assert self.is_pending, "can not flush when not pending"
            self._cancel_timer()
            self._invoke()


class TkThrottleWrapper[**P, T](TkDebounceWrapper[P, T]):
    def __init__(self, widget: Misc, func: Callable[P, T], ms: int, *, leading: bool = False, trailing: bool = True):
        super().__init__(widget, func, ms, leading=leading, trailing=trailing)

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        with self.lock:
            if self.is_pending:
                self._update_pending_args(args, kwargs)
                return
            super().__call__(*args, **kwargs)


def tk_debounce(widget: Misc, ms: int, *, leading=False, trailing=True):
    """
    基于 Tkinter 的防抖函数。
    设计与实现参考自 https://github.com/toss/es-toolkit/blob/main/src/function/debounce.ts。

    :param widget: Tkinter 组件或窗口
    :param ms: 延迟的毫秒数。
    :param leading: 在超时前沿调用。
    :param trailing: 在超时后沿调用。
    """

    def decorator[T, **P](func: Callable[P, T]) -> TkDebounceWrapper[P, T]:
        wrapper = TkDebounceWrapper(widget, func, ms, leading=leading, trailing=trailing)
        return wrapper

    return decorator


def tk_throttle(widget: Misc, ms: int, *, leading=False, trailing=True):
    """
    基于 Tkinter 的节流函数。
    设计与实现参考自 https://github.com/toss/es-toolkit/blob/main/src/function/throttle.ts。

    :param widget: Tkinter 组件或窗口
    :param ms: 延迟的毫秒数。
    :param leading: 在超时前沿调用。
    :param trailing: 在超时后沿调用。
    """

    def decorator[T, **P](func: Callable[P, T]) -> TkThrottleWrapper:
        wrapper = TkThrottleWrapper(widget, func, ms, leading=leading, trailing=trailing)
        return wrapper

    return decorator


def debounce_throttle_example():
    from tkinter import Tk
    from tkinter.ttk import Button, Label

    i = 1
    tk = Tk()
    tk.resizable(False, False)
    tk.configure(padx="3p", pady="3p")

    label = Label(tk, text=f"i = {i}", anchor="center", width=20)
    label.grid_configure(column=0, row=0, rowspan=2)

    debounce_btn = Button(tk, text="debounce i += 1")
    debounce_btn.grid_configure(column=1, row=0, sticky="nsew", ipadx="4p", ipady="4p", pady="4p")
    cancel_debounce_btn = Button(tk, text="Cancel")
    cancel_debounce_btn.grid_configure(column=2, row=0, sticky="nsew", ipadx="4p", ipady="4p", pady="4p")
    throttle_btn = Button(tk, text="throttle i += 1")

    throttle_btn.grid_configure(column=1, row=1, sticky="nsew", ipadx="4p", ipady="4p", pady="4p")
    cancel_throttle_btn = Button(tk, text="Cancel")
    cancel_throttle_btn.grid_configure(column=2, row=1, sticky="nsew", ipadx="4p", ipady="4p", pady="4p")

    @tk_debounce(debounce_btn, 1000)
    def on_debounce_click():
        nonlocal i
        i += 1
        label.configure(text=f"i = {i}")

    debounce_btn.configure(command=on_debounce_click)
    cancel_debounce_btn.configure(command=on_debounce_click.cancel)

    @tk_throttle(debounce_btn, 500)
    def on_throttle_click():
        nonlocal i
        i += 1
        label.configure(text=f"i = {i}")

    throttle_btn.configure(command=on_throttle_click)
    cancel_throttle_btn.configure(command=on_throttle_click.cancel)

    tk.mainloop()


if __name__ == "__main__":
    debounce_throttle_example()
