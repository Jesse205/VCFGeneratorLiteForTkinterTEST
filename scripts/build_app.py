import argparse
from glob import iglob
import os
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import zipapp
from zipfile import ZipFile

import PyInstaller.__main__ as pyinstaller
from prepare_innosetup_extensions import PATH_INNOSETUP_EXTENSION, prepare_innosetup_extensions

from vcf_generator_lite.__version__ import __version__ as APP_VERSION
from vcf_generator_lite.constants import APP_COPYRIGHT

PYTHON_VERSION = sysconfig.get_python_version()
PLATFORM_PYTHON = f"{sys.implementation.name}-{PYTHON_VERSION}"
PLATFORM_NATIVE = sysconfig.get_platform()
OUTPUT_BASE_NAME_TEMPLATE = "VCFGeneratorLite-v{version}-{variant}"


def ensure_dist_dir():
    if not os.path.isdir("dist"):
        os.mkdir("dist")


def require_pyinstaller_output():
    if not os.path.isdir(os.path.join("dist", "vcf_generator_lite")):
        raise RuntimeError("PyInstaller build not found.")


def build_with_pyinstaller():
    print("Building with PyInstaller...")
    ensure_dist_dir()
    pyinstaller.run(["vcf_generator_lite.spec", "--noconfirm"])
    print("Building finished.")


def build_with_uv():
    uv_path = shutil.which("uv")
    if uv_path is None:
        print("uv not found.", file=sys.stderr)
        sys.exit(1)
    subprocess.run([uv_path, "build"], check=True)


def build_with_pdm_packer():
    print("Building with pdm-packer...")
    ensure_dist_dir()
    pdm_path = shutil.which("pdm")
    if pdm_path is None:
        print("pdm not found.", file=sys.stderr)
        return 1
    subprocess.run(
        [
            pdm_path,
            "pack",
            "-m",
            "vcf_generator_lite.__main__:main",
            "-o",
            os.path.join(
                "dist",
                OUTPUT_BASE_NAME_TEMPLATE.format(version=APP_VERSION, variant="py3") + ".pyzw",
            ),
            "--interpreter",
            "/usr/bin/env python3",
            "--compress",
        ],
        env={
            **os.environ,
            "PYTHONOPTIMIZE": "2",
        },
        check=True,
    )
    print("Building finished.")


def pack_with_innosetup():
    print("Packaging with InnoSetup...")
    require_pyinstaller_output()
    if not os.path.isdir(PATH_INNOSETUP_EXTENSION):
        if (result := prepare_innosetup_extensions()) != 0:
            return result

    search_path = os.environ["PATH"] + os.pathsep + "C:\\Program Files (x86)\\Inno Setup 6\\"
    iscc_path = shutil.which("iscc", path=search_path)
    if iscc_path is None:
        print("InnoSetup not found.", file=sys.stderr)
        sys.exit(1)

    architectures_allowed = "x86compatible"
    architectures_install_in64_bit_mode = ""

    match PLATFORM_NATIVE:
        case "win-amd64":
            architectures_allowed = "x64compatible"
            architectures_install_in64_bit_mode = "win64"
        case "win-arm64":
            architectures_allowed = "arm64"
            architectures_install_in64_bit_mode = "win64"
        case _:
            raise ValueError(f"Invalid platform: {PLATFORM_NATIVE}")

    subprocess.run(
        [
            iscc_path,
            "/D"
            + f"OutputBaseFilename={
                OUTPUT_BASE_NAME_TEMPLATE.format(version=APP_VERSION, variant=f'{PLATFORM_NATIVE}-setup')
            }",
            "/D" + f"MyAppCopyright={APP_COPYRIGHT}",
            "/D" + f"MyAppVersion={APP_VERSION}",
            "/D" + f"ArchitecturesAllowed={architectures_allowed}",
            "/D" + f"ArchitecturesInstallIn64BitMode={architectures_install_in64_bit_mode}",
            os.path.abspath("vcf_generator_lite.iss"),
        ],
        check=True,
    )
    print("Packaging finished.")


def pack_with_zipfile():
    print("Packaging with ZipFile...")
    require_pyinstaller_output()
    zip_path = os.path.join(
        "dist",
        OUTPUT_BASE_NAME_TEMPLATE.format(version=APP_VERSION, platform=f"{PLATFORM_NATIVE}-portable") + ".zip",
    )
    with ZipFile(zip_path, "w") as zip_file:
        for path, _dirs, files in os.walk(os.path.join("dist", "vcf_generator_lite")):
            for file_path in [os.path.join(path, file) for file in files]:
                zip_file.write(file_path, os.path.relpath(file_path, "dist"))
    print("Packaging finished.")


def build_with_zipapp():
    zipapp_path = Path("build/zipapp")
    site_packages_path = zipapp_path / "site-packages"
    if zipapp_path.is_dir():
        shutil.rmtree(zipapp_path)
    elif zipapp_path.is_file():
        os.remove(zipapp_path)
    export_result = subprocess.run(
        ["uv", "export", "--no-dev", "--no-editable"],
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["uv", "pip", "sync", "-", "--target", site_packages_path],
        input=export_result.stdout,
        text=True,
        check=True,
    )

    # 清理无用内容
    shutil.rmtree(site_packages_path / "bin")
    os.remove(site_packages_path / ".lock")
    for info_dirs in iglob(str(site_packages_path / "*.dist-info")):
        for file in Path(info_dirs).iterdir():
            if file.name not in ("METADATA", "licenses"):
                if file.is_file():
                    file.unlink()
                else:
                    shutil.rmtree(file)

    zipapp.create_archive(
        site_packages_path,
        target=os.path.join(
            "dist",
            OUTPUT_BASE_NAME_TEMPLATE.format(version=APP_VERSION, variant="py3") + ".pyzw",
        ),
        main="vcf_generator_lite.__main__:main",
        compressed=True,
    )

    print("Building finished.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        default="innosetup",
        choices=["innosetup", "portable", "zipapp"],
        help="软件包类型（默认：%(default)s）",
    )
    args = parser.parse_args()

    type_ = args.type
    match type_:
        case "innosetup":
            build_with_pyinstaller()
            pack_with_innosetup()
        case "portable":
            build_with_pyinstaller()
            pack_with_zipfile()
        case "zipapp":
            build_with_zipapp()
        case _:
            raise ValueError(f"Invalid type: {type_}")


if __name__ == "__main__":
    main()
