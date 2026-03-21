import argparse
import logging
import os
import sys

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import URL_REPOSITORY
from vcf_generator_lite.ui.windows.main_window import create_app
from vcf_generator_lite.utils.dpi_aware import enable_dpi_aware
from vcf_generator_lite.utils.locales import t

try:
    from colorlog import ColoredFormatter
except ImportError:
    ColoredFormatter = None

APP_DESCRIPTION = "Makes one vCard from a contact list."


def fix_home_env():
    """
    修复 Tkinter 在 Windows 中无法获取 HOME 的问题
    """
    os.environ["HOME"] = os.path.expanduser("~")


def setup_logging():
    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    log_format = "{asctime} {levelname:8} {name:50.50} {message}"
    if ColoredFormatter:
        formatter = ColoredFormatter("{log_color}" + log_format, style="{")
    else:
        formatter = logging.Formatter(log_format, style="{")

    handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.DEBUG if __debug__ else logging.INFO,
        handlers=[handler],
    )


def setup_common_parser(parser: argparse.ArgumentParser):
    parser.description = t("app.description")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"vcf-generator-lite {__version__}",
    )


def setup_gui_parser(parser: argparse.ArgumentParser):
    setup_common_parser(parser)


def launch_gui(args: argparse.Namespace):
    setup_logging()
    fix_home_env()
    enable_dpi_aware()

    logging.info("Starting VCF Generator...")
    print(t("startup.source_tip").format(url=URL_REPOSITORY))

    app, _ = create_app()
    app.mainloop()

    logging.info("Exiting VCF Generator...")


def main_gui():
    parser = argparse.ArgumentParser()
    setup_gui_parser(parser)
    args = parser.parse_args()
    launch_gui(args)


def main():
    main_gui()


if __name__ == "__main__":
    main()
