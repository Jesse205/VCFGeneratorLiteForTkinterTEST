import argparse
import sys
# noinspection PyPep8Naming
import PyInstaller.__main__ as PyInstaller

from scripts.utils import get_bits


def pyinstaller():
    PyInstaller.run(["vcf_generator.spec", "--noconfirm"])


def main():
    if get_bits() != 64:
        print(f"Only 64 bit python is supported. Current version is {get_bits()}.", file=sys.stderr)
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--builder", type=str, default="pyinstaller", choices=["pyinstaller"])
    args = parser.parse_args()

    builder = args.builder

    if builder == "pyinstaller":
        pyinstaller()
    else:
        print(f"Unknown builder: {builder}", file=sys.stderr)
        exit(1)
