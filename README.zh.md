<div align="center">
<img src="./docs/images/icon.svg" width="192" alt="App icon" />

# VCF 生成器 Lite

**仓库：**
[![Gitee 仓库](https://img.shields.io/badge/Gitee-仓库-C71D23?logo=gitee)][RepositoryOnGitee]
[![GitHub 仓库](https://img.shields.io/badge/GitHub-仓库-0969da?logo=github)][RepositoryOnGithub]

**平台：**
[![Windows7+（exe）](https://img.shields.io/badge/Windows_7+-exe-0078D4?logo=windows)][ReleaseOnGitee]
[![Python3.12+（pyzw）](https://img.shields.io/badge/Python_3.12+-pyzw-3776AB?logo=python&logoColor=f5f5f5)][ReleaseOnGitee]

**语言：**
**中文** |
[English](./README.md) |
<small>期待您的翻译！</small>

_该应用程序目前仅支持中文。_

</div>

VCF 生成器，输入姓名与手机号则自动生成用于批量导入到通讯录内的 VCF 文件。

[![许可证](https://img.shields.io/github/license/HelloTool/VCFGeneratorLiteForTkinter?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](./LICENSE)
[![贡献者公约](https://img.shields.io/badge/贡献者公约-2.1-4baaaa.svg)](./docs/CODE_OF_CONDUCT.zh.md)

## 软件截图

<img src="./docs/images/screenshots/main_window.webp" width="600" alt="主窗口" />

## 下载

### 应用分发形式

根据使用场景选择最适合的部署方式：

| 分发形式 | 运行方式                    | 适用场景                  |
| -------- | --------------------------- | ------------------------- |
| 安装器   | 通过安装程序安装后使用      | 长期使用/需要桌面快捷方式 |
| 便携包   | 解压即用（支持U盘随身携带） | 免安装/临时使用           |
| Zip 应用 | 双击直接运行                | 快速启动/跨平台使用       |

<!-- | Chocolatey         | 命令行一键部署              | 自动化安装/集中管理/快速版本更新 |
| Android 应用软件包 | 安装后使用                  | 移动设备使用/临时处理需求        |
| 网站               | 进入网站即可运行            | 临时使用/跨平台使用              | -->

### 环境要求

不同的应用包有一不同环境要求，您需要根据您的系统环境选择对应的应用包。

| 软件包类型    | 运行时依赖              | 架构要求 | 前置条件                           |
| ------------- | ----------------------- | -------- | ---------------------------------- |
| 安装器/便携包 | Windows 7+ 系统环境     | x86_64   | Windows 7 需补丁文件（见下方说明） |
| Zip 应用      | Python 3.12+ 与 Tkinter | 无限制   | 需安装 Python 3.12+ 与 Tkinter     |

<!-- | Chocolatey         | Chocolatey 2.0.0       | x86_64   | 需安装 Chocolatey                            |
| Android 应用软件包 | Android 系统环境       | 未知     | Windows 11 需安装 WSA，Linux 需安装 Waydroid |
| 网站               | 浏览器                 | 无限制   | 需安装浏览器                                 | -->

注：您还需要与运行时依赖兼容的环境。

### 文件下载列表

通过以下渠道获取软件包：

- [Gitee 发行版][ReleaseOnGitee]
- [GitHub Releases][ReleaseOnGithub]

各系统对应文件清单：

| 软件包类型 | Windows               | Linux                   | macOS                   | Android |
| ---------- | --------------------- | ----------------------- | ----------------------- | ------- |
| 安装器     | `*_setup.exe`（推荐） | 暂未提供                | 暂未提供                | 不支持  |
| 便携包     | `*_portable.zip`      | 暂未提供                | 暂未提供                | 不支持  |
| Zip 应用   | `*_zipapp.pyzw`       | `*_zipapp.pyzw`（推荐） | `*_zipapp.pyzw`（推荐） | 不支持  |

<!-- | Chocolatey         | 暂未提供                  | 不支持                            | 不支持                            | 不支持           |
| Android 应用软件包 | 暂未提供                  | 暂未提供                          | 不支持                            | 暂未提供（推荐） |
| 网站               | 暂未提供                  | 暂未提供                          | 不支持                            | 暂未提供         | -->

### Windows 7 特别说明

<details>
<summary>兼容性补丁安装指南（仅 Windows 7 用户）</summary>

1. **获取 Python 嵌入包**：从 [PythonWin7][PythonWin7RepositoryOnGithub] 仓库下载：
    - `python-3.13.2-embed-amd64.zip`
2. **提取 DLL 文件**：解压下载的 ZIP 包，从中获取以下文件：
    - `python313.dll`  
    - `api-ms-win-core-path-l1-1-0.dll`
3. **应用补丁**：
    1. 完成软件安装
    2. 打开安装目录下的 `_internal` 文件夹
    3. 将下载的两个 DLL 文件覆盖到该目录

</details>

## 使用方法

1. 把名字和电话以每行 `姓名 电话号码` 的格式复制到下面的编辑框内；
   ```text
   李四	13445467890
   王五	13554678907
   赵六	13645436748
   ```
2. 点击“生成”，选择一个路径保存文件；
3. 将生成后的 VCF 文件复制到手机内，打开文件时选择使用“通讯录”，然后根据提示操作；
4. 等待导入完成。

> [!NOTE]
>
> - 制表符将会自动转换为空格处理。
> - 程序会自动去除输入框内多余的空格。
> - 如果每行有多个空格，则会将最后一个空格以前所有的字符当作姓名处理。
>
> 比如 ` Wang lei   13333333333   ` 将会被识别为
>
> ```text
> 姓名：Wang lei
> 电话：13333333333
> ```

## 开发与贡献

请参阅[《开发指南》](./docs/dev/README.md)与[《贡献指南》](./docs/CONTRIBUTING.md)。

## 许可证

本项目以 Apache 2.0 许可证发布，详情请参阅 [LICENSE](./LICENSE)。

```txt
Copyright 2023-2025 Jesse205

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 开源声明

| 项目                                  | 许可证                                | 目的                           |
| ------------------------------------- | ------------------------------------- | ------------------------------ |
| [Python][CPythonRepository]           | [Python license][CPythonLicense]      | 提供运行时环境                 |
| [UPX][UPXRepository]                  | [UPX license][UPXLicense]             | 压缩代码                       |
| [PyInstaller][PyInstallerRepository]  | [GPL-2.0 license][PyInstallerLicense] | 打包为 APP                     |
| [tkhtmlview][TkhtmlviewRepository]    | [MIT License][TkhtmlviewLicense]      | 显示 HTML 内容（已修改源代码） |
| [TtkText][TtkTextRepository]          | [MIT License][TtkTextLicense]         | 提供现代UI的富文本编辑器       |

[RepositoryOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/
[RepositoryOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/
[ReleaseOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[ReleaseOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[PythonWin7RepositoryOnGithub]: https://github.com/adang1345/PythonWin7

[PythonHomepage]: https://www.python.org/
[CPythonRepository]: https://github.com/python/cpython
[CPythonLicense]: https://docs.python.org/3/license.html
[UPXRepository]: https://github.com/upx/upx
[UPXLicense]: https://github.com/upx/upx/blob/devel/LICENSE
[PyInstallerRepository]: https://github.com/pyinstaller/pyinstaller
[PyInstallerLicense]: https://pyinstaller.org/en/stable/license.html
[TkhtmlviewRepository]: https://github.com/bauripalash/tkhtmlview
[TkhtmlviewLicense]: https://github.com/bauripalash/tkhtmlview/blob/main/LICENSE
[TtkTextRepository]: https://github.com/Jesse205/TtkText
[TtkTextLicense]: https://github.com/Jesse205/TtkText/blob/main/LICENSE
