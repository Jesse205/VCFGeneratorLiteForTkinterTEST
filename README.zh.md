<div align="center">
<img src="./vcf_generator/assets/icon.png" width="192"/>

# VCF 生成器 Lite

[![Gitee 仓库](https://img.shields.io/badge/Gitee-仓库-C71D23?logo=gitee)](https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter)

[![Windows](https://img.shields.io/badge/Windows-exe-%232863C5?logo=windows)][ReleaseInGitee]

**中文** |
[English](./README.md) |
<small>期待你的翻译！</small>

_应用程序暂时只支持中文_

</div>

VCF 生成器，输入姓名与手机号则自动生成用于批量导入到通讯录内的 VCF 文件。

[![许可证：MIT](https://img.shields.io/badge/许可证-MIT-green)](./LICENSE)
[![贡献者公约](https://img.shields.io/badge/贡献者公约-2.1-4baaaa.svg)](./CODE_OF_CONDUCT.zh.md)

## 软件截图

<img src="./screenshots/Snipaste_2024-06-17_04-06-51.png" width="600" alt="Snipaste_2024-06-17_04-06-51.png" />

## 使用方法

进入[发行版][ReleaseInGitee]下载并运行安装程序（文件名通常是 `VCFGenerator_<版本>_<Python版本>_<处理器架构>_64_setup.exe`）。

1. 把名字和电话以每行` 姓名 电话号码` 的格式复制到下面的编辑框内；
   ```text
   李四	13445467890
   王五	13554678907
   赵六	13645436748
   ```
2. 点击“生成”，选择一个路径保存文件；
3. 将生成后的 VCF 文件复制到手机内，打开文件时选择使用“通讯录”，然后根据提示操作。
4. 等待导入完成

> [!TIP]
>
> - 制表符将会自动转换为空格处理。
> - 程序会自动去除输入框内多余的空格。
> - 如果每行有多个空格，则会将最后一个空格以前所有的字符当作姓名处理。\
>   比如 `Wang lei 13333333333` 将会识别为
>   ```text
>   姓名：Wang lei
>   电话：13333333333
>   ```

## 软件架构

- `vcf_generator`：源代码目录
    - `console`：开发 CLI
    - `ui`： GUI 用户界面
    - `util`：工具类
    - `widget`：Tkinter 组件
    - `constants.py`：常量
- `assets`：资源文件目录
- `main.py`：程序入口

## 开发项目

> [!NOTE]
>
> 开发环境目前仅支持 64 位 Windows 7+，暂不支持 macOS 与 Linux。

### 构建项目

1. 安装 [Python 3.8+](https://www.python.org/)、[Poetry](https://python-poetry.org/)、[UPX](https://upx.github.io/)、[InnoSetup](https://jrsoftware.org/isinfo.php)
2. 在 [Inno Setup Translations](https://jrsoftware.org/files/istrans/) 网站下载并安装安装 `ChineseSimplified.isl`
3. 安装项目：`poetry install`
4. 生成 `file_version_info.txt`：`poetry run generate-version-file`
5. 生成应用的二进制文件：`poetry run build-app`
6. 生成安装程序：`poetry run build-setup`

### 切换版本

运行 `poetry run change-version <版本名>`

## 许可

本项目以 [MIT 许可](./LICENSE)开源

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)（作为应用图标使用）：MIT license
- [Python](https://www.python.org/)：[Python license](https://docs.python.org/3/license.html)
- [UPX](https://upx.github.io/)：GPL-2.0 licenses
- [PyInstaller](https://pyinstaller.org/en/stable/)：[PyInstaller license](https://pyinstaller.org/en/stable/license.html)
- [Nuitka](https://nuitka.net/)：Apache-2.0 license
- [tkhtmlview](https://github.com/bauripalash/tkhtmlview)：MIT License

[ReleaseInGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
