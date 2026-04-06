import argparse
import contextlib
import logging
import os
import sys
from pathlib import Path

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.utils.locales import t

__all__ = ["main"]


def setup_logging(verbose: bool):
    try:
        import colorlog
    except ImportError:
        colorlog = None

    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    log_format = "{asctime} {levelname:8} {name:50.50} {message}"
    if colorlog:
        formatter = colorlog.ColoredFormatter("{log_color}" + log_format, style="{")
    else:
        formatter = logging.Formatter(log_format, style="{")

    handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        handlers=[handler],
    )


def fix_home_env():
    """修复 Tkinter 在 Windows 中无法获取 HOME 的问题"""
    with contextlib.suppress(RuntimeError):
        os.environ["HOME"] = str(Path.home())


def launch(*, quiet: bool, verbose: bool):
    from vcf_generator_lite.constants import URL_REPOSITORY
    from vcf_generator_lite.ui.windows.main_window import create_app
    from vcf_generator_lite.utils.dpi_aware import enable_dpi_aware

    if quiet:
        sys.stdout = None
    setup_logging(verbose=verbose)
    fix_home_env()
    enable_dpi_aware()

    print(t("startup.source_tip").format(url=URL_REPOSITORY))

    app, _controller = create_app()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description=t("app.description"),
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help=t("cli.help_option_quiet"),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=t("cli.help_option_verbose"),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{t('app.name')} {__version__}",
    )
    args = parser.parse_args()
    launch(quiet=args.quiet, verbose=args.verbose)


if __name__ == "__main__":
    main()
