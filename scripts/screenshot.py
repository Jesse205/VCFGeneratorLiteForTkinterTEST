"""生成多平台、多语言的界面截图（父进程：设置语言并调度场景子进程）。"""

import argparse
import contextlib
import subprocess
import sys
from pathlib import Path

from scripts.screenshot_config import LANGUAGES, PLATFORM_NAMES, set_language

# Windows 系统级字体覆盖用的族名（标题栏由系统绘制，进程内设置无法影响）。
WINDOWS_SYSTEM_FONT = "Noto Sans CJK SC"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("all", *LANGUAGES), default="all", help="界面语言")
    parser.add_argument("--platform", choices=tuple(PLATFORM_NAMES.values()), help="目标平台，默认自动检测")
    parser.add_argument("--output-dir", type=Path, default=Path("screenshots"), help="输出目录")
    parser.add_argument("--font-dir", type=Path, help="含 Noto 字体的目录（临时注册，退出还原）")
    parser.add_argument("--scale", type=float, default=2.0, help="缩放倍率")
    parser.add_argument("--wait", type=float, default=1.0, help="每次截图前的渲染等待秒数")
    parser.add_argument("--ttk-theme", default="clam", help="ttk 主题名（Linux）")
    parser.add_argument("--theme-dir", action="append", default=[], help="外部 ttk 主题目录（可重复）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    platform = args.platform or PLATFORM_NAMES.get(sys.platform)
    if platform is None:
        raise SystemExit(f"不支持的平台：{sys.platform}")

    if platform == "linux":
        # 进程级：在 Tk 窗口创建前配置 X 资源与窗口管理器，只做一次（子进程继承显示环境）。
        from scripts.screenshot_linux_env import configure_environment

        configure_environment()

    with contextlib.ExitStack() as stack:
        if args.font_dir is not None:
            # 字体注册：Windows 会话级 / Unix 用户级；退出时按备份还原，不留残留。
            from scripts.screenshot_windows import FontsInstalled

            stack.enter_context(FontsInstalled(args.font_dir))

        languages = LANGUAGES if args.lang == "all" else (args.lang,)
        for lang in languages:
            set_language(lang)
            # 系统级覆盖：Windows 需临时改系统字体/DPI（标题栏由系统绘制），退出时自动还原。
            if platform == "windows":
                from scripts.screenshot_windows import WindowsSystemSettings

                system_settings = WindowsSystemSettings(WINDOWS_SYSTEM_FONT, args.scale)
            else:
                system_settings = contextlib.nullcontext()

            with system_settings:
                command = [
                    sys.executable,
                    "-m",
                    "scripts.screenshot_scene",
                    "--lang",
                    lang,
                    "--platform",
                    platform,
                    "--output-dir",
                    str(args.output_dir),
                    "--scale",
                    str(args.scale),
                    "--wait",
                    str(args.wait),
                    "--ttk-theme",
                    args.ttk_theme,
                    *([item for directory in args.theme_dir for item in ("--theme-dir", directory)]),
                ]
                subprocess.run(command, check=True)  # ruff: ignore[subprocess-without-shell-equals-true]


if __name__ == "__main__":
    main()
