<div align="center">
<img src="./docs/images/icon.png" width="192"/>

# VCF 生成器 Lite

[![Gitee 仓库](https://img.shields.io/badge/Gitee-仓库-C71D23?logo=gitee)][RepositoryOnGitee]
[![GitHub 仓库](https://img.shields.io/badge/GitHub-仓库-0969da?logo=github)][RepositoryOnGithub]

[![Windows exe](https://img.shields.io/badge/Windows-exe-0078D4?logo=windows)][ReleaseOnGitee]
[![Python pyzw](https://img.shields.io/badge/Python-pyzw-3776AB?logo=python&logoColor=f5f5f5)][ReleaseOnGitee]

**中文** |
[English](./README.md) |
<small>期待你的翻译！</small>

_该应用程序目前仅支持中文。_

</div>

VCF 生成器，输入姓名与手机号则自动生成用于批量导入到通讯录内的 VCF 文件。

[![许可证](https://img.shields.io/github/license/HelloTool/VCFGeneratorLiteForTkinter?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](./LICENSE)
[![贡献者公约](https://img.shields.io/badge/贡献者公约-2.1-4baaaa.svg)](./CODE_OF_CONDUCT.zh.md)

## 软件截图

<img src="./docs/images/screenshots/Snipaste_2025-01-13_06-08-40.png" width="600" alt="Snipaste_2025-01-13_06-08-40.png" />

## 环境要求

- `VCFGenerator_<版本>_<位数>_setup.exe`、`VCFGenerator_<版本>_<位数>_bin_windows.zip`
    - 操作系统：Windows 8+ 或 Windows 7+（伴随补丁）
    - CPU：x86 64位
- `vcf_generator.pyzw`
    - 操作系统：Windows 8+ 或 Windows 7+（伴随补丁）（其他操作系统暂不支持）
    - Python 版本：Python 3.13（伴随 Tkinter）

对于部分系统，您可以通过修补软件的方法支持运行此 APP。如需在这些系统中运行此 APP，请参考[修补 APP](#修补-APP)章节。

### 修补 APP

<details>
<summary>支持 Windows 7 运行</summary>

1. 下载兼容 Windows 7 的 `python313.dll` 与 `api-ms-win-core-path-l1-1-0.dll`；
    - 您可以选择到 [PythonWin7][PythonWin7RepositoryOnGithub] 仓库中下载这两个文件。
2. 安装软件，进入安装目录中 `_internal`，覆盖以上两个 DLL。

</details>

## 使用方法

1. 进入[发行版][ReleaseOnGitee]下载并安装 APP；
2. 打开 APP；
3. 把名字和电话以每行 `姓名 电话号码` 的格式复制到下面的编辑框内；
    ```text
    李四	13445467890
    王五	13554678907
    赵六	13645436748
    ```
4. 点击“生成”，选择一个路径保存文件；
5. 将生成后的 VCF 文件复制到手机内，打开文件时选择使用“通讯录”，然后根据提示操作；
6. 等待导入完成。

> [!NOTE]
>
> - 制表符将会自动转换为空格处理。
> - 程序会自动去除输入框内多余的空格。
> - 如果每行有多个空格，则会将最后一个空格以前所有的字符当作姓名处理。
>
> 比如 ` Wang lei   13333333333   ` 将会被识别为
> ```text
> 姓名：Wang lei
> 电话：13333333333
> ```

## 项目结构

- `src`：源代码目录
    - `vcf_generator_lite/ui`： GUI 用户界面
    - `vcf_generator_lite/util`：工具类
    - `vcf_generator_lite/widget`：Tkinter 组件
    - `vcf_generator_lite/constants.py`：常量
    - `vcf_generator_lite/assets`：资源文件目录
    - `__main__.py`：程序入口
- `scripts`：脚本目录
- `pyproject.toml`：项目配置文件
- `setup.iss`：InnoSetup 配置文件，用于生成 Windows 安装器
- `vcf_generator_lite.spec`：PyInstaller 配置文件，用于构建 APP
- `metadata.yml`：信息文件（不包括版本），用于生成 versionfile.txt
- `versionfile.txt`：自动生成的信息文件，为 PyInstaller 提供 EXE 信息

## 开发项目

> [!TIP]
>
> 您可以通过 `pdm run --list` 查看所有本项目定义命令。

### 开发准备

1. 安装 [Python 3.13+](https://www.python.org/)、[PDM](https://pdm-project.org/zh-cn/latest/)、[UPX](https://upx.github.io/)、[InnoSetup 6.4](https://jrsoftware.org/isinfo.php)；
2. 安装项目依赖：`pdm install`；
3. 安装 PDM 插件：`pdm install --plugins`；
4. 下载 InnoSetup 文件：`pdm run prepare_innosetup_extensions`。

### 构建应用

运行 `pdm run build_app`。

### 切换版本

运行 `pdm run version <版本名>`。

## 许可

本项目以 [MIT 许可](./LICENSE)开源。

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)（作为应用图标使用）：MIT license
- [Python](https://www.python.org/)：[Python license](https://docs.python.org/3/license.html)
- [UPX](https://upx.github.io/)（用于压缩代码）：GPL-2.0 license
- [PyInstaller](https://pyinstaller.org/en/stable/)（用于打包为 APP）：[GPL-2.0 license](https://pyinstaller.org/en/stable/license.html)
- [tkhtmlview](https://github.com/bauripalash/tkhtmlview)：MIT License

## 贡献项目

请参阅 [《贡献指南》](./CONTRIBUTING.zh.md)。

[RepositoryOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/
[RepositoryOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/
[ReleaseOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[ReleaseOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[PythonWin7RepositoryOnGithub]: https://github.com/adang1345/PythonWin7
