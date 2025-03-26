import argparse
import os
import shutil
import subprocess
import sys
import sysconfig
from zipfile import ZipFile

import PyInstaller.__main__ as pyinstaller

from scripts.prepare_innosetup_extensions import PATH_INNOSETUP_EXTENSION, main as prepare_innosetup_extensions
from scripts.utils import require_64_bits
from vcf_generator_lite.__version__ import __version__ as APP_VERSION
from vcf_generator_lite.constants import APP_COPYRIGHT

PYTHON_VERSION = sysconfig.get_python_version()
PLATFORM_PYTHON = f"{sys.implementation.name}-{PYTHON_VERSION}"
PLATFORM_NATIVE = sysconfig.get_platform()
OUTPUT_BASE_NAME_TEMPLATE = "VCFGeneratorLite_v{version}_{platform}_{distribution}"


def ensure_dist_dir():
    if not os.path.isdir("dist"):
        os.mkdir("dist")


def ensure_pyinstaller_output():
    if not os.path.isdir(os.path.join("dist", "vcf_generator_lite")):
        raise RuntimeError("PyInstaller build not found.")


def build_with_pyinstaller():
    print("Building with PyInstaller...")
    ensure_dist_dir()
    pyinstaller.run(["vcf_generator_lite.spec", "--noconfirm"])
    print("Building finished.")


def build_with_pdm_packer():
    print("Building with pdm-packer...")
    ensure_dist_dir()
    os.environ["PYTHONOPTIMIZE"] = "2"
    result = subprocess.run([
        shutil.which("pdm"),
        "pack",
        "-m", "vcf_generator_lite.__main__:main",
        "-o", os.path.join("dist", OUTPUT_BASE_NAME_TEMPLATE.format(
            version=APP_VERSION,
            platform=PLATFORM_PYTHON,
            distribution="zipapp"
        ) + ".pyzw"),
        "--interpreter", f"/usr/bin/env python{PYTHON_VERSION}",
        "--compile",
        "--compress",
        "--no-py",
    ])
    print("Building finished.")
    return result.returncode


def pack_with_innosetup() -> int:
    print("Packaging with InnoSetup...")
    ensure_pyinstaller_output()
    if not os.path.isdir(PATH_INNOSETUP_EXTENSION):
        if (result := prepare_innosetup_extensions()) != 0:
            return result

    os.environ["PATH"] += os.pathsep + "C:\\Program Files (x86)\\Inno Setup 6\\"
    result = subprocess.run([
        shutil.which("iscc"),
        "/D" + f"OutputBaseFilename={OUTPUT_BASE_NAME_TEMPLATE.format(
            version=APP_VERSION,
            platform=PLATFORM_NATIVE,
            distribution="setup"
        )}",
        "/D" + f"MyAppCopyright={APP_COPYRIGHT}",
        "/D" + f"MyAppVersion={APP_VERSION}",
        os.path.abspath('setup.iss'),
    ])
    print("Packaging finished.")
    return result.returncode


def pack_with_zipfile():
    print("Packaging with ZipFile...")
    ensure_pyinstaller_output()
    zip_path = os.path.join("dist", OUTPUT_BASE_NAME_TEMPLATE.format(
        version=APP_VERSION,
        platform=PLATFORM_NATIVE,
        distribution="portable"
    ) + ".zip")
    with ZipFile(zip_path, "w") as zip_file:
        for path, dirs, files in os.walk(os.path.join("dist", "vcf_generator_lite")):
            for file_path in [os.path.join(path, file) for file in files]:
                zip_file.write(file_path, os.path.relpath(file_path, "dist"))
    print("Packaging finished.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--type",
        type=str,
        default="installer",
        choices=["installer", "portable", "zipapp"],
        help="应用打包类型（默认：%(default)s）"
    )
    args = parser.parse_args()

    type_ = args.type
    match type_:
        case "installer":
            require_64_bits()
            build_with_pyinstaller()
            return pack_with_innosetup()
        case "portable":
            require_64_bits()
            build_with_pyinstaller()
            pack_with_zipfile()
        case "zipapp":
            return build_with_pdm_packer()
    return 0
