import argparse
import subprocess

import requests

LINK_INSTALLER = "https://files.jrsoftware.org/is/6/innosetup-{version}.exe"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", type=str, default="6.4.0")
    args = parser.parse_args()

    version = args.version
    response = requests.get(LINK_INSTALLER.format(version=version), stream=True)
    # with open(f"/innosetup-{version}.exe", "wb") as f:
    #     for chunk in response.iter_content(chunk_size=1024):
    #         if chunk:
    #             f.write(chunk)
    subprocess.run([f"/innosetup-{version}.exe","/SILENT", "/ALLUSERS","/SUPPRESSMSGBOXES","/SP"])
    return 0
