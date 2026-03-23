import argparse
import sys
from typing import TextIO

from vcf_generator_lite.core.vcf_generator import GenerateResult
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


def print_result(result: GenerateResult, output_path: str | None):
    if result.exception:
        print(t("cli.info_generation_error").format(exception=result.exception))
    elif len(result.invalid_items) > 0:
        if output_path:
            print(t("cli.info_generation_invalid").format(path=output_path))
        else:
            print(t("cli.info_generation_invalid_stdout"))
    else:
        if output_path:
            print(t("cli.info_generation_success").format(path=output_path))
        else:
            print(t("cli.info_generation_success_stdout"))

    print()
    print(t("cli.info_success_count").format(count=result.saved_count))
    print(t("cli.info_invalid_count").format(count=len(result.invalid_items)))
    print(t("cli.info_time_elapsed").format(time=result.time_elapsed))

    if result.invalid_items:
        print()
        print(t("cli.info_invalid_items_detail"))
        for item in result.invalid_items:
            print(
                t("cli.info_line").format(
                    row=item.row_position,
                    raw_content=item.raw_content,
                    exception=item.exception,
                )
            )


def launch_cli(args: argparse.Namespace):
    from vcf_generator_lite.core.vcf_generator import VCFGeneratorTask

    input_io: TextIO | None = None
    output_io: TextIO | None = None
    if args.input:
        input_io = open(args.input, encoding="utf8")
    if args.output:
        output_io = open(args.output, mode="w", encoding="utf8")

    try:
        if input_io is None:
            print(t("cli.prompt_contact_list").format(finish_keys="Ctrl+Z"))

        task = VCFGeneratorTask(input_text=(input_io or sys.stdin).read(), output_io=output_io or sys.stdout)
        task.start()
        task.join()
    finally:
        if input_io:
            input_io.close()
        if output_io:
            output_io.close()
    result = task.result
    if result is None:
        print(t("cli.info_generation_cancelled"))
        return
    print_result(result, args.output)


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
