import argparse
import contextlib
import os
from pathlib import Path

from vcf_generator_lite.utils.locales import t


def fix_home_env():
    """修复 Tkinter 在 Windows 中无法获取 HOME 的问题"""
    with contextlib.suppress(RuntimeError):
        os.environ["HOME"] = str(Path.home())


def get_gui_parent_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        parents=[],
        add_help=False,
    )


def launch_gui(_args: argparse.Namespace):
    from vcf_generator_lite.constants import URL_REPOSITORY
    from vcf_generator_lite.ui.windows.main_window import create_app
    from vcf_generator_lite.utils.dpi_aware import enable_dpi_aware

    fix_home_env()
    enable_dpi_aware()

    print(t("startup.source_tip").format(url=URL_REPOSITORY))

    app, _controller = create_app()
    app.mainloop()


def main_gui():
    from vcf_generator_lite.entries.common import get_common_parent_parser, setup_common

    parser = argparse.ArgumentParser(
        parents=[
            get_common_parent_parser(),
            get_gui_parent_parser(),
        ],
        description=t("app.description"),
    )
    args = parser.parse_args()

    setup_common(args)
    launch_gui(args)


if __name__ == "__main__":
    main_gui()
