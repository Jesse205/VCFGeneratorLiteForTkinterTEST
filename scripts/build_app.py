import argparse
import os
import shutil
import subprocess
import sys
import sysconfig
import zipapp
from pathlib import Path
from zipfile import ZipFile

import packaging.version
import PyInstaller.__main__ as pyinstaller
from prepare_innosetup_extensions import PATH_INNOSETUP_EXTENSION, prepare_innosetup_extensions

from vcf_generator_lite.__version__ import __version__
from vcf_generator_lite.constants import APP_COPYRIGHT

PYTHON_VERSION = sysconfig.get_python_version()
PLATFORM_PYTHON = f"{sys.implementation.name}-{PYTHON_VERSION}"
PLATFORM_NATIVE = sysconfig.get_platform()

DISTRIBUTION_ZIPAPP_NAME = f"VCFGeneratorLite-v{__version__}-py3.pyzw"
DISTRIBUTION_SETUP_BASE_NAME = f"VCFGeneratorLite-v{__version__}-{PLATFORM_NATIVE}-setup"
DISTRIBUTION_PORTABLE_NAME = f"VCFGeneratorLite-v{__version__}-{PLATFORM_NATIVE}-portable.zip"

PATH_DIST = Path("dist").resolve()
PATH_BUILD = Path("build").resolve()


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


app_windows_version = ".".join(str(part) for part in get_windows_file_info_version(__version__))


def ensure_dist_dir():
    if not PATH_DIST.is_dir():
        PATH_DIST.mkdir(parents=True, exist_ok=True)


def require_pyinstaller_output():
    if not PATH_DIST.joinpath("vcf_generator_lite").is_dir():
        raise RuntimeError("PyInstaller build not found.")


def build_with_pyinstaller():
    print("Building with PyInstaller...")
    ensure_dist_dir()
    pyinstaller.run(["vcf_generator_lite.spec", "--noconfirm"])
    print("Building finished.")


def build_with_uv():
    subprocess.run(["uv", "build"], check=True)  # noqa: S607


def pack_with_innosetup():
    print("Packaging with InnoSetup...")
    require_pyinstaller_output()

    if not PATH_INNOSETUP_EXTENSION.is_dir():
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

    subprocess.run(  # noqa: S603
        [
            iscc_path,
            "/D" + f"OutputBaseFilename={DISTRIBUTION_SETUP_BASE_NAME}",
            "/D" + f"MyAppCopyright={APP_COPYRIGHT}",
            "/D" + f"MyAppVersion={__version__}",
            "/D" + f"VersionInfoVersion={app_windows_version}",
            "/D" + f"ArchitecturesAllowed={architectures_allowed}",
            "/D" + f"ArchitecturesInstallIn64BitMode={architectures_install_in64_bit_mode}",
            Path("vcf_generator_lite.iss").absolute(),
        ],
        check=True,
    )
    print("Packaging finished.")


def pack_with_zipfile():
    print("Packaging with ZipFile...")
    require_pyinstaller_output()
    with ZipFile(PATH_DIST.joinpath(DISTRIBUTION_PORTABLE_NAME), "w") as zip_file:
        PATH_DIST.joinpath("vcf_generator_lite")
        for path, _dirs, files in os.walk(PATH_DIST.joinpath("vcf_generator_lite")):
            for file_path in (Path(path, file) for file in files):
                zip_file.write(file_path, os.path.relpath(file_path, "dist"))
    print("Packaging finished.")


def build_with_zipapp():
    ensure_dist_dir()
    zipapp_path = PATH_BUILD / "zipapp"
    site_packages_path = zipapp_path / "site-packages"
    if zipapp_path.is_dir():
        shutil.rmtree(zipapp_path)
    elif zipapp_path.is_file():
        zipapp_path.unlink()
    export_result = subprocess.run(
        ["uv", "export", "--no-dev", "--no-editable"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(  # noqa: S603
        ["uv", "pip", "sync", "--no-cache", "--target", site_packages_path, "--link-mode", "copy", "-"],  # noqa: S607
        input=export_result.stdout,
        text=True,
        check=True,
    )

    # 清理无用内容
    if (bin_path := site_packages_path / "bin").is_dir():
        shutil.rmtree(bin_path)
    site_packages_path.joinpath(".lock").unlink()
    site_packages_path.glob("*.dist-info")
    for info_dir_paths in site_packages_path.glob("*.dist-info"):
        for file in info_dir_paths.iterdir():
            if file.name not in ("METADATA", "licenses"):
                if file.is_file():
                    file.unlink()
                else:
                    shutil.rmtree(file)

    archive_path = PATH_DIST.joinpath(DISTRIBUTION_ZIPAPP_NAME)
    if archive_path.exists():
        archive_path.unlink()
    zipapp.create_archive(
        site_packages_path,
        target=archive_path,
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
