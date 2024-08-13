import argparse
import re

from typing import List, Pattern

from scripts import generateVersionFile


def get_exe_style_version(version: str):
    assert re.match(r"^(\d+\.)*\d+$", version), f"Invalid version: {version}"
    version_list: List[str] = version.split(".")
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
        file_name="vcf_generator/__init__.py",
        content_pattern=re.compile("# VERSION\n.*\n# END-VERSION"),
        content_formatter='# VERSION\n__version__ = "%s"\n# END-VERSION',
        version=version
    )


def change_pyproject_version(version: str):
    change_version(
        file_name="pyproject.toml",
        content_pattern=re.compile("# VERSION\n.*\n# END-VERSION"),
        content_formatter='# VERSION\nversion = "%s"\n# END-VERSION',
        version=version
    )


def change_setup_version(version: str):
    change_version(
        file_name="setup.iss",
        content_pattern=re.compile("; VERSION\n.*\n; END-VERSION"),
        content_formatter='; VERSION\n#define MyAppVersion "%s"\n; END-VERSION',
        version=version,
        encoding="gbk"
    )


def change_metadata_version(version: str):
    change_version(
        file_name="metadata.yml",
        content_pattern=re.compile("# VERSION\n.*\n# END-VERSION"),
        content_formatter='# VERSION\nVersion: %s\n# END-VERSION',
        version=get_exe_style_version(version)
    )
    generateVersionFile.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str)
    args = parser.parse_args()

    version = args.version
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print("Invalid version format. Version must be like '1.2.3'.")
        return
    change_init_version(version)
    change_pyproject_version(version)
    change_setup_version(version)
    change_metadata_version(version)
