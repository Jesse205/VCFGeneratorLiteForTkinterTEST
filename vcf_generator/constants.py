APP_NAME = "VCF 生成器 Lite"
APP_OPEN_SOURCE_LICENSES = [
    {"name": "tkhtmlview", "url": "https://github.com/bauripalash/tkhtmlview", "license": "MIT License"},
    {"name": "CPython", "url": "https://github.com/python/cpython",
     "license": "Python Software Foundation License Version 2"},
    {"name": "pyinstaller", "url": "https://github.com/pyinstaller/pyinstaller",
     "license": "The PyInstaller licensing terms"},
    {"name": "nuitka", "url": "https://github.com/Nuitka/Nuitka",
     "license": "Apache License Version 2.0, January 2004"},
]
APP_DETAILS_OPEN_SOURCE_LICENSES = [
    f"<a href=\"{_license['url']}\">{_license['name']}</a> - {_license['license']}<br />" for _license in
    APP_OPEN_SOURCE_LICENSES
]
APP_COPYRIGHT = "Copyright (c) 2023-2024 Jesse205"

URL_RELEASES = "https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases"
URL_SOURCE = "https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter"

EMAIL_JESSE205 = "jesse205@qq.com"

APP_DETAILS = f"""<h6>链接</h6>
源代码：<a href="{URL_SOURCE}">{URL_SOURCE}</a><br />
版本发布：<a href="{URL_RELEASES}">{URL_RELEASES}</a><br />
<h6>联系作者</h6>
电子邮件：<a href="mailto:{EMAIL_JESSE205}">{EMAIL_JESSE205}</a>
<h6>开源许可证</h6>
{''.join(APP_DETAILS_OPEN_SOURCE_LICENSES)}
"""

DEFAULT_INPUT_CONTENT = """张三	13345367789
李四	13445467890
王五	13554678907
赵六	13645436748
"""

USAGE = """使用说明：
1. 把名字和电话以每行“姓名 电话号码”的格式复制到下面的编辑框内；
2. 点击“生成”，选择一个路径保存文件；
3. 将生成后的 VCF 文件复制到手机内，打开文件时选择使用“通讯录”，然后根据提示操作。
4. 等待导入完成"""
