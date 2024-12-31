import os
import re
import sys

import requests

URL_CHINESE_SIMPLIFIED_ISL_URL = "https://raw.github.com/jrsoftware/issrc/main/Files/Languages/Unofficial/ChineseSimplified.isl"
# 国内使用 GitCode 加速下载
URL_CHINESE_SIMPLIFIED_ISL_GITCODE = "https://raw.gitcode.com/gh_mirrors/is/issrc/raw/main/Files/Languages/Unofficial/ChineseSimplified.isl"

PATH_INNOSETUP_EXTENSION = ".innosetup"
PATH_CHINESE_SIMPLIFIED = os.path.join(PATH_INNOSETUP_EXTENSION, "Languages", "ChineseSimplified.isl")

TEXT_REPLACE_DICT_CHINESE_SIMPLIFIED = {
    "PrivilegesRequiredOverrideText2": "仅为您安装 %1，或为所有用户安装(需要管理员权限)。"
}


def main() -> int:
    print("Preparing InnoSetup extensions.")
    response = requests.get(URL_CHINESE_SIMPLIFIED_ISL_GITCODE)
    if response.status_code != 200:
        print(f"Failed to download Chinese Simplified ISL: {response.status_code}", file=sys.stderr)
        return 1
    file_text = response.text
    # 获取到的内容是CRLF换行的，但是python只能识别LF换行，所以需要替换一下
    file_text = file_text.replace("\r", "")
    for key, value in TEXT_REPLACE_DICT_CHINESE_SIMPLIFIED.items():
        file_text = re.sub(f"^{key}=.*$", f"{key}={value}", file_text, flags=re.MULTILINE)
    os.makedirs(os.path.dirname(PATH_CHINESE_SIMPLIFIED), exist_ok=True)
    # TODO: 解决文件换行不一致问题
    with open(PATH_CHINESE_SIMPLIFIED, "wt", encoding=response.encoding, newline="\r\n") as f:
        f.write(file_text)
    print("Downloaded Chinese Simplified ISL.")
    return 0
