import argparse
import logging
import sys

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.utils.locales import t


def setup_logging(verbose: bool):
    try:
        from colorlog import ColoredFormatter
    except ImportError:
        # noinspection PyPep8Naming
        ColoredFormatter = None

    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    log_format = "{asctime} {levelname:8} {name:50.50} {message}"
    if ColoredFormatter:
        formatter = ColoredFormatter("{log_color}" + log_format, style="{")
    else:
        formatter = logging.Formatter(log_format, style="{")

    handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        handlers=[handler],
    )


def get_common_parent_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help=t("cli.verbose_help"),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{t('app.name')} {__version__}",
    )
    return parser


def setup_common(args: argparse.Namespace):
    setup_logging(args.verbose)
