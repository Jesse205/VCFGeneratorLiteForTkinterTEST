import argparse
import subprocess
import sys

# noinspection PyPep8Naming
import PyInstaller.__main__ as PyInstaller

from scripts.utils import get_bits


def build_with_pyinstaller():
    PyInstaller.run(["vcf_generator.spec", "--noconfirm"])


def build_with_zipapp():
    subprocess.run(["pdm", "pack   -m vcf_generator.__main__:main --pyc --no-py -c", "-o", "app.pyzw"])


def main():
    if get_bits() != 64:
        print(f"Only 64 bit python is supported. Current version is {get_bits()}.", file=sys.stderr)
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--builder", type=str, default="pyinstaller", choices=["pyinstaller", "zipapp"])
    args = parser.parse_args()

    builder = args.builder

    if builder == "pyinstaller":
        build_with_pyinstaller()
    elif builder == "zipapp":
        build_with_zipapp()
    else:
        print(f"Unknown builder: {builder}", file=sys.stderr)
        exit(1)
