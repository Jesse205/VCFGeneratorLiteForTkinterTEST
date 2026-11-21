"""在 Xvfb + dbus 会话内配置截图环境（Xft DPI、光标、xfwm4 装饰）。

须在 Tk 窗口创建前调用一次；由截图父进程调度，避免每个语言子进程重复启动窗口管理器。
"""

import os
import shutil
import subprocess
import time

DEFAULTS = {
    "SHOT_DPI": "192",
    "SHOT_WM_THEME": "Default-xhdpi",
    "SHOT_BUTTON_LAYOUT": "O|HMC",
    "SHOT_TITLE_FONT": "Noto Sans 18",
}


def _executable(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise SystemExit(f"未找到可执行文件：{name}")
    return path


def _run(*command: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [_executable(command[0]), *command[1:]],
        input=input_text,
        text=True,
        capture_output=True,
        check=check,
    )


def _set_xfwm4_property(name: str, value_type: str, value: str) -> None:
    _run("xfconf-query", "-c", "xfwm4", "-p", name, "-n", "-t", value_type, "-s", value)


def _wait_for_xfconfd() -> None:
    for _ in range(50):
        if _run("xfconf-query", "-c", "xfwm4", "-l", check=False).returncode == 0:
            return
        time.sleep(0.1)


def _wait_for_window_manager() -> None:
    for _ in range(50):
        result = _run("xprop", "-root", "_NET_SUPPORTING_WM_CHECK", check=False)
        if "window id" in result.stdout:
            return
        time.sleep(0.1)


def configure_environment() -> None:
    """写 X 资源（DPI、光标常亮）并启动配置好的 xfwm4。"""
    dpi = os.environ.get("SHOT_DPI", DEFAULTS["SHOT_DPI"])
    theme = os.environ.get("SHOT_WM_THEME", DEFAULTS["SHOT_WM_THEME"])
    layout = os.environ.get("SHOT_BUTTON_LAYOUT", DEFAULTS["SHOT_BUTTON_LAYOUT"])
    title_font = os.environ.get("SHOT_TITLE_FONT", DEFAULTS["SHOT_TITLE_FONT"])

    # Xft.dpi 影响 Xft/fontconfig 渲染；insertOffTime 是 Tk Text 的资源名（驼峰），
    # 设为 0 使插入光标常亮，避免在 widget 级侵入式 configure。
    _run("xrdb", "-merge", input_text=f"Xft.dpi: {dpi}\n*Text.insertOffTime: 0\n")

    _wait_for_xfconfd()
    _set_xfwm4_property("/general/theme", "string", theme)
    _set_xfwm4_property("/general/title_font", "string", title_font)
    _set_xfwm4_property("/general/title_alignment", "string", "left")
    _set_xfwm4_property("/general/button_layout", "string", layout)
    _set_xfwm4_property("/general/use_compositing", "bool", "false")
    _set_xfwm4_property("/general/show_frame_shadow", "bool", "false")
    _set_xfwm4_property("/general/show_popup_shadow", "bool", "false")

    subprocess.Popen([_executable("xfwm4")])  # ruff: ignore[subprocess-without-shell-equals-true]
    _wait_for_window_manager()
