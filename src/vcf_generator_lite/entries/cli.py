import argparse
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import TextIO

from vcf_generator_lite.core.vcf_generator import GenerateResult
from vcf_generator_lite.utils.locales import t


def get_cli_parent_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        parents=[],
        add_help=False,
    )
    parser.add_argument(
        "-i",
        "--input",
        help=t("cli.help_option_input"),
        required=sys.stdin is None,
    )
    parser.add_argument(
        "-o",
        "--output",
        help=t("cli.help_option_output"),
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
    elif output_path:
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
                ),
            )


def launch_cli(args: argparse.Namespace):
    from vcf_generator_lite.core.vcf_generator import VCFGeneratorTask

    with ExitStack() as stack:
        input_io: TextIO | None = None
        output_io: TextIO | None = None
        input_io = stack.enter_context(Path(args.input).open(encoding="utf8")) if args.input else sys.stdin
        output_io = (
            stack.enter_context(Path(args.output).open(mode="w", encoding="utf8")) if args.output else sys.stdout
        )
        if input_io is None or output_io is None:
            sys.exit(1)

        if not args.input:
            print(t("cli.prompt_contact_list").format(finish_keys="Ctrl+Z"))

        task = VCFGeneratorTask(input_text=input_io.read(), output_io=output_io)
        task.start()
        task.join()

    result = task.result
    if result is None:
        print(t("cli.info_generation_stopped"))
        return
    print_result(result, args.output)


def main_cli():
    from vcf_generator_lite.entries.common import get_common_parent_parser, setup_common

    parser = argparse.ArgumentParser(
        parents=[
            get_common_parent_parser(),
            get_cli_parent_parser(),
        ],
        description=t("app.description"),
    )
    args = parser.parse_args()

    setup_common(args)
    launch_cli(args)


if __name__ == "__main__":
    main_cli()
