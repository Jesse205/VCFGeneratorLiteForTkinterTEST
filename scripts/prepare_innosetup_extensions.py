import argparse
import os
import sys

import requests

URL_CHINESE_SIMPLIFIED_ISL_URL = "https://raw.github.com/jrsoftware/issrc/main/Files/Languages/Unofficial/ChineseSimplified.isl"
URL_CHINESE_SIMPLIFIED_ISL_LATEST = "https://github.com/kira-96/Inno-Setup-Chinese-Simplified-Translation/raw/refs/heads/main/ChineseSimplified.isl"
# 国内使用 GitCode 加速下载
URL_CHINESE_SIMPLIFIED_ISL_GITCODE = "https://raw.gitcode.com/gh_mirrors/is/issrc/raw/main/Files/Languages/Unofficial/ChineseSimplified.isl"

PATH_INNOSETUP_EXTENSION = "./.innosetup"
PATH_CHINESE_SIMPLIFIED = os.path.join(
    PATH_INNOSETUP_EXTENSION, "Languages", "ChineseSimplified.isl"
)


def prepare_innosetup_extensions(
    download_url: str = URL_CHINESE_SIMPLIFIED_ISL_LATEST,
) -> int:
    print("Preparing InnoSetup extensions.")
    response = requests.get(download_url)
    if response.status_code != 200:
        print(
            f"Failed to download Chinese Simplified ISL: {response.status_code}",
            file=sys.stderr,
        )
        return 1
    file_text = response.text
    # 获取到的内容是CRLF换行的，但是python只能识别LF换行，所以需要替换一下
    file_text = file_text.replace("\r", "")

    os.makedirs(os.path.dirname(PATH_CHINESE_SIMPLIFIED), exist_ok=True)
    with open(
        PATH_CHINESE_SIMPLIFIED, "wt", encoding=response.encoding, newline="\r\n"
    ) as f:
        f.write(file_text)
    print("Downloaded Chinese Simplified ISL.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mirror",
        type=str,
        default="latest",
        choices=["github", "gitcode", "latest"],
        help="文件下载镜像（默认：%(default)s）",
    )
    args = parser.parse_args()
    match args.mirror:
        case "github":
            download_url = URL_CHINESE_SIMPLIFIED_ISL_URL
        case "latest":
            download_url = URL_CHINESE_SIMPLIFIED_ISL_LATEST
        case "gitcode":
            download_url = URL_CHINESE_SIMPLIFIED_ISL_GITCODE
        case _:
            download_url = URL_CHINESE_SIMPLIFIED_ISL_URL
    return prepare_innosetup_extensions(download_url)
