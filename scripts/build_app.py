import argparse
import sys

# noinspection PyPep8Naming
import PyInstaller.__main__ as PyInstaller

from scripts.utils import get_bits


def build_with_pyinstaller():
    PyInstaller.run(["vcf_generator.spec", "--noconfirm"])


def build_with_zipapp():
    # TODO: 支持zipapp打包
    pass


def main() -> int:
    if get_bits() != 64:
        print(f"Only 64 bit python is supported. Current version is {get_bits()}.", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--builder", type=str, default="pyinstaller", choices=["pyinstaller"])
    args = parser.parse_args()

    builder = args.builder

    if builder == "pyinstaller":
        build_with_pyinstaller()
    elif builder == "zipapp":
        build_with_zipapp()
    return 0
