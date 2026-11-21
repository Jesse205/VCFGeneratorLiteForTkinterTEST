"""场景子进程：初始化翻译后创建窗口并截图。

必须在导入依赖 gettext 的模块之前调用 setup_l10n，因此单独成进程。
"""

import argparse
from pathlib import Path

from scripts.screenshot_config import set_language


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True, choices=("en-US", "zh-CN"))
    parser.add_argument("--platform", required=True, choices=("windows", "macos", "linux"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument("--wait", type=float, required=True)
    parser.add_argument("--ttk-theme", required=True)
    parser.add_argument("--theme-dir", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    set_language(args.lang)

    from vcf_generator_lite.bootstrap import setup_l10n

    setup_l10n()

    if args.platform == "windows":
        from vcf_generator_lite.utils.platform.windows.dpi_aware import enable_dpi_aware

        enable_dpi_aware()

    from scripts.screenshot_window import capture_language

    capture_language(
        output_dir=args.output_dir,
        platform=args.platform,
        lang=args.lang,
        ttk_theme=args.ttk_theme,
        theme_dirs=args.theme_dir,
        scale=args.scale,
        wait=args.wait,
    )


if __name__ == "__main__":
    main()
