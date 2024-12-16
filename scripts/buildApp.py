import argparse
import os

from scripts.utils import get_bits

def pyinstaller():
    os.system("pyinstaller vcf_generator.spec --noconfirm")


def main():
    if get_bits() != 64:
        print(f"Only 64 bit python is supported. Current version is {get_bits()}")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("-builder", "--builder", type=str, default="pyinstaller")
    args = parser.parse_args()

    builder = args.builder
    if builder not in ["pyinstaller"]:
        print(f"Unknown builder: {builder}")
        return
    elif builder == "pyinstaller":
        pyinstaller()
