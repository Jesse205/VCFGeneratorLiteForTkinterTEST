import argparse
import os

from vcf_generator_lite.utils.locales import t


def fix_home_env():
    """
    修复 Tkinter 在 Windows 中无法获取 HOME 的问题
    """
    os.environ["HOME"] = os.path.expanduser("~")


def get_gui_parent_parser() -> argparse.ArgumentParser:
    from vcf_generator_lite.entries.common import get_common_parent_parser

    parser = argparse.ArgumentParser(
        parents=[get_common_parent_parser()],
        add_help=False,
    )
    return parser


def launch_gui(args: argparse.Namespace):
    from vcf_generator_lite.constants import URL_REPOSITORY
    from vcf_generator_lite.ui.windows.main_window import create_app
    from vcf_generator_lite.utils.dpi_aware import enable_dpi_aware

    fix_home_env()
    enable_dpi_aware()

    print(t("startup.source_tip").format(url=URL_REPOSITORY))

    app, _ = create_app()
    app.mainloop()


def main_gui():
    from vcf_generator_lite.entries.common import setup_common

    parser = argparse.ArgumentParser(
        parents=[get_gui_parent_parser()],
        description=t("app.description"),
    )
    args = parser.parse_args()

    setup_common(args)
    launch_gui(args)


if __name__ == "__main__":
    main_gui()
