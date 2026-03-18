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
import packaging.version
from prepare_innosetup_extensions import PATH_INNOSETUP_EXTENSION, prepare_innosetup_extensions

from vcf_generator_lite.__version__ import __version__ as APP_VERSION
from vcf_generator_lite.constants import APP_COPYRIGHT

PYTHON_VERSION = sysconfig.get_python_version()
PLATFORM_PYTHON = f"{sys.implementation.name}-{PYTHON_VERSION}"
PLATFORM_NATIVE = sysconfig.get_platform()

DISTRIBUTION_ZIPAPP_NAME = f"VCFGeneratorLite-v{APP_VERSION}-py3.pyzw"
DISTRIBUTION_SETUP_BASE_NAME = f"VCFGeneratorLite-v{APP_VERSION}-{PLATFORM_NATIVE}-setup"
DISTRIBUTION_PORTABLE_NAME = f"VCFGeneratorLite-v{APP_VERSION}-{PLATFORM_NATIVE}-portable.zip"


def get_windows_file_info_version(version: str) -> tuple[int, int, int, int]:
    parsed = packaging.version.parse(version)
    build = 0
    match parsed.pre:
        case ("a", _):
            build += 10000
        case ("b", _):
            build += 20000
        case ("rc", _):
            build += 30000
        case _:
            if not parsed.is_devrelease:
                build += 40000
    if parsed.pre:
        build += parsed.pre[1] * 100
    if parsed.post is not None:
        build += parsed.post * 10
    if parsed.dev is not None:
        build += parsed.dev
    return (
        parsed.major,
        parsed.minor,
        parsed.micro,
        build,
    )


app_windows_version = ".".join(str(part) for part in get_windows_file_info_version(APP_VERSION))


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


def pack_with_innosetup():
    print("Packaging with InnoSetup...")
    require_pyinstaller_output()
    if not os.path.isdir(PATH_INNOSETUP_EXTENSION):
        prepare_innosetup_extensions()

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
            "/D" + f"OutputBaseFilename={DISTRIBUTION_SETUP_BASE_NAME}",
            "/D" + f"MyAppCopyright={APP_COPYRIGHT}",
            "/D" + f"MyAppVersion={APP_VERSION}",
            "/D" + f"VersionInfoVersion={app_windows_version}",
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
    zip_path = os.path.join("dist", DISTRIBUTION_PORTABLE_NAME)
    with ZipFile(zip_path, "w") as zip_file:
        for path, _dirs, files in os.walk(os.path.join("dist", "vcf_generator_lite")):
            for file_path in [os.path.join(path, file) for file in files]:
                zip_file.write(file_path, os.path.relpath(file_path, "dist"))
    print("Packaging finished.")


def build_with_zipapp():
    ensure_dist_dir()
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
        ["uv", "pip", "sync", "-", "--no-cache", "--target", site_packages_path],
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
        target=os.path.join("dist", DISTRIBUTION_ZIPAPP_NAME),
        main="vcf_generator_lite.__main__:main",
        interpreter="/usr/bin/env python3",
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
