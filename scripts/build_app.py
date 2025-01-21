import argparse
import os
import shutil
import subprocess
import sys
from zipfile import ZipFile

# noinspection PyPep8Naming
import PyInstaller.__main__ as PyInstaller

from scripts.prepare_innosetup_extensions import PATH_INNOSETUP_EXTENSION, main as prepare_innosetup_extensions
from scripts.utils import get_bits
from vcf_generator_lite import __version__ as app_version
from vcf_generator_lite.constants import APP_COPYRIGHT

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
OUTPUT_BASE_NAME = f"VCFGeneratorLite_v{app_version}_{get_bits()}bit"


def build_with_pyinstaller():
    print("Building with PyInstaller...")
    PyInstaller.run(["vcf_generator_lite.spec", "--noconfirm"])
    print("Building finished.")


def build_with_zipapp():
    print("Building with pdm-packer...")
    result = subprocess.run([
        shutil.which("pdm"),
        "pack",
        "-m", "vcf_generator_lite.__main__:main",
        "-o", "dist/vcf_generator_lite.pyzw",
        "--interpreter", "/usr/bin/env python3.13",
        "--compile",
        "--compress",
        "--no-py",
    ])
    print("Building finished.")
    return result.returncode


def pack_with_innosetup() -> int:
    print("Packaging with InnoSetup...")
    if not os.path.isdir(PATH_INNOSETUP_EXTENSION):
        if result := prepare_innosetup_extensions():
            return result
    os.environ["PATH"] += os.pathsep + "C:\\Program Files (x86)\\Inno Setup 6\\"
    result = subprocess.run([
        shutil.which("iscc"),
        "/D" + f"OutputBaseFilename={OUTPUT_BASE_NAME}_setup",
        "/D" + f"MyAppCopyright={APP_COPYRIGHT}",
        "/D" + f"MyAppVersion={app_version}",
        os.path.abspath('setup.iss'),
    ])
    print("Packaging finished.")
    return result.returncode


def pack_with_zipfile():
    print("Packaging with ZipFile...")
    with ZipFile(os.path.join("dist", f"{OUTPUT_BASE_NAME}_bin_windows.zip"), "w") as zip_file:
        for path, dirs, files in os.walk(os.path.join("dist", "vcf_generator_lite")):
            for file_path in [os.path.join(path, file) for file in files]:
                zip_file.write(file_path, os.path.relpath(file_path, "dist"))
    print("Packaging finished.")


def main() -> int:
    if get_bits() != 64:
        print(f"Only 64 bit python is supported. Current version is {get_bits()}.", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="bundle", choices=["bundle", "zipfile", "zipapp"])
    args = parser.parse_args()

    type_ = args.type
    match type_:
        case "bundle":
            build_with_pyinstaller()
            return pack_with_innosetup()
        case "zipfile":
            build_with_pyinstaller()
            pack_with_zipfile()
        case "zipapp":
            build_with_zipapp()
    return 0
