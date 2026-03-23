import argparse
import sys
from typing import TextIO

from vcf_generator_lite.utils.locales import t


def get_cli_input(file_path: str | None) -> TextIO:
    if file_path:
        return open(file_path, encoding="utf8")
    elif sys.stdin is not None:
        return sys.stdin
    raise ValueError("没有任何输入源")


def get_cli_output(file_path: str | None) -> TextIO:
    if file_path:
        return open(file_path, mode="w", encoding="utf8")
    elif sys.stdout is not None:
        return sys.stdout
    raise ValueError("没有任何输出源")


def get_cli_parent_parser() -> argparse.ArgumentParser:
    from vcf_generator_lite.entries.common import get_common_parent_parser

    parser = argparse.ArgumentParser(
        parents=[get_common_parent_parser()],
        add_help=False,
    )
    parser.add_argument(
        "-i",
        "--input",
        help="输入文件路径",
        required=sys.stdin is None,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出文件路径",
        required=sys.stdout is None,
    )
    return parser


def launch_cli(args: argparse.Namespace):
    from vcf_generator_lite.core.vcf_generator import VCFGeneratorTask

    with get_cli_input(args.input) as input_io, get_cli_output(args.output) as output_io:
        input_io = get_cli_input(args.input)
        output_io = get_cli_output(args.output)
        if input_io.isatty():
            print("请以每行“姓名 号码 备注”（备注可忽略）的格式输入（按 Ctrl+Z 可结束）：")

        task = VCFGeneratorTask(input_text=input_io.read(), output_io=output_io)
        task.start()
        task.join()


def main_cli():
    from vcf_generator_lite.entries.common import setup_common

    parser = argparse.ArgumentParser(
        parents=[get_cli_parent_parser()],
        description=t("app.description"),
    )
    args = parser.parse_args()

    setup_common(args)
    launch_cli(args)


if __name__ == "__main__":
    main_cli()
