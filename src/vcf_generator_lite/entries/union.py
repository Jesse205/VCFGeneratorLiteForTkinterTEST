import argparse

from vcf_generator_lite.entries.cli import launch_cli
from vcf_generator_lite.utils.locales import t


def get_union_parent_parser() -> argparse.ArgumentParser:
    from vcf_generator_lite.entries.common import get_common_parent_parser
    from vcf_generator_lite.entries.gui import get_gui_parent_parser

    parser = argparse.ArgumentParser(parents=[get_common_parent_parser()], add_help=False)
    subparsers = parser.add_subparsers(help="启动模式", dest="launch_mode")
    subparsers.add_parser(
        "cli",
        parents=[],
        help=t("cli.cli_help"),
        description=t("cli.cli_help"),
    )
    subparsers.add_parser(
        "gui",
        parents=[get_gui_parent_parser()],
        help=t("cli.gui_help"),
        description=t("cli.gui_help"),
    )
    return parser


def main():
    from vcf_generator_lite.entries.common import setup_common
    from vcf_generator_lite.entries.gui import launch_gui

    parser = argparse.ArgumentParser(
        parents=[get_union_parent_parser()],
        description=t("app.description"),
    )
    args = parser.parse_args()
    setup_common(args)

    if args.launch_mode == "cli":
        launch_cli(args)
    else:
        launch_gui(args)


if __name__ == "__main__":
    main()
