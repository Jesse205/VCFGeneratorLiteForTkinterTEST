import logging
import os
import sys

from vcf_generator_lite import constants
from vcf_generator_lite.utils.dpi_aware import enable_dpi_aware
from vcf_generator_lite.utils.locales import scope
from vcf_generator_lite.windows.main import create_app

try:
    from colorlog import ColoredFormatter
except ImportError:
    ColoredFormatter = None

startup_t = scope("startup")


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


def main():
    setup_logging()
    fix_home_env()
    enable_dpi_aware()

    logging.info("Starting VCF Generator...")
    print(startup_t("source_tip").format(url=constants.URL_REPOSITORY))

    app, _ = create_app()

    app.mainloop()

    logging.info("Exiting VCF Generator...")


if __name__ == "__main__":
    main()
