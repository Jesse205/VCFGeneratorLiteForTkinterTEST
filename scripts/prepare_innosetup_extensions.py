import argparse
import os
import sys

import requests

URL_CHINESE_SIMPLIFIED_ISL_URL = (
    "https://raw.github.com/jrsoftware/issrc/main/Files/Languages/Unofficial/ChineseSimplified.isl"
)
URL_CHINESE_SIMPLIFIED_ISL_LATEST = (
    "https://github.com/kira-96/Inno-Setup-Chinese-Simplified-Translation/raw/refs/heads/main/ChineseSimplified.isl"
)
# 国内使用 GitCode 加速下载
# ***** GitCode!

PATH_INNOSETUP_EXTENSION = "./.innosetup"
PATH_CHINESE_SIMPLIFIED = os.path.join(PATH_INNOSETUP_EXTENSION, "Languages", "ChineseSimplified.isl")


def prepare_innosetup_extensions(
    download_url: str = URL_CHINESE_SIMPLIFIED_ISL_LATEST,
):
    print("Preparing InnoSetup extensions.")
    response = requests.get(download_url)
    if response.status_code != 200:
        print(
            f"Failed to download Chinese Simplified ISL: {response.status_code}",
            file=sys.stderr,
        )
        sys.exit(1)
    file_text = response.text
    # 获取到的内容是 CRLF 换行的，但是 python 只能识别 LF 换行，所以需要替换一下
    file_text = file_text.replace("\r", "")

    os.makedirs(os.path.dirname(PATH_CHINESE_SIMPLIFIED), exist_ok=True)
    with open(PATH_CHINESE_SIMPLIFIED, "wt", encoding=response.encoding, newline="\r\n") as f:
        f.write(file_text)
    print("Downloaded Chinese Simplified ISL.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mirror",
        type=str,
        default="latest",
        choices=["github", "latest"],
        help="文件下载镜像（默认：%(default)s）",
    )
    args = parser.parse_args()
    match args.mirror:
        case "github":
            download_url = URL_CHINESE_SIMPLIFIED_ISL_URL
        case "latest":
            download_url = URL_CHINESE_SIMPLIFIED_ISL_LATEST
        case _:
            download_url = URL_CHINESE_SIMPLIFIED_ISL_URL
    prepare_innosetup_extensions(download_url)


if __name__ == "__main__":
    main()
