"""场景子进程：初始化翻译后创建窗口并截图。

必须在导入依赖 gettext 的模块之前调用 setup_l10n，因此单独成进程。
"""

import argparse
from pathlib import Path

from scripts.screenshot_config import set_language


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True, choices=("en-US", "zh-CN"))
    parser.add_argument("--platform", required=True, choices=("macos", "linux"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--font-family", required=True)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument("--wait", type=float, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    set_language(args.lang)

    from vcf_generator_lite.bootstrap import setup_l10n

    setup_l10n()

    from scripts.screenshot_window import capture_language

    capture_language(
        output_dir=args.output_dir,
        platform=args.platform,
        lang=args.lang,
        font_family=args.font_family,
        scale=args.scale,
        wait=args.wait,
    )


if __name__ == "__main__":
    main()
