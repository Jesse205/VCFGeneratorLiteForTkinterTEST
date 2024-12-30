import argparse
import re
import sys
from typing import Pattern

import pyinstaller_versionfile


def get_exe_style_version(version: str):
    assert re.match(r"^(\d+\.)*\d+$", version), f"Invalid version: {version}"
    version_list: list[str] = version.split(".")
    while len(version_list) < 4:
        version_list.append("0")
    return ".".join(version_list[0:4])


def change_version(
    file_name: str,
    content_pattern: Pattern[str],
    content_formatter: str,
    version: str,
    encoding="utf-8"
):
    with open(file_name, "r", encoding=encoding) as f:
        origin_content = f.read()
    new_content = re.sub(content_pattern, content_formatter % version, origin_content)
    with open(file_name, "w", encoding=encoding) as f:
        f.write(new_content)
    print("Change version to %s in %s." % (version, file_name))


def change_init_version(version: str):
    change_version(
        file_name="./src/vcf_generator/__init__.py",
        content_pattern=re.compile(r'^ *__version__ *= *".*" *$', flags=re.M),
        content_formatter='__version__ = "%s"',
        version=version
    )


def change_pyproject_version(version: str):
    change_version(
        file_name="pyproject.toml",
        content_pattern=re.compile(r'^ *version *= *".*" *$', flags=re.M),
        content_formatter='version = "%s"',
        version=version
    )


def change_setup_version(version: str):
    change_version(
        file_name="setup.iss",
        content_pattern=re.compile(r'^ *#define *MyAppVersion *".*" *$', flags=re.M),
        content_formatter='#define MyAppVersion "%s"',
        version=version,
        encoding="gbk"
    )


def change_version_info(version: str):
    pyinstaller_versionfile.create_versionfile_from_input_file(
        output_file="versionfile.txt",
        input_file="metadata.yml",
        version=get_exe_style_version(version)
    )
    print("Change version to %s in %s." % (version, "versionfile.txt"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str)
    args = parser.parse_args()

    version = args.version
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print("Invalid version format. Version must be like '1.2.3'.", file=sys.stderr)
        return 1
    change_init_version(version)
    change_pyproject_version(version)
    change_setup_version(version)
    change_version_info(version)
