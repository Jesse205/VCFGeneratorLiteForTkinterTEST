<div align="center">
<img src="./docs/images/icon.svg" width="192" alt="App icon" />

# VCF 生成器 Lite

**仓库**：
[![Gitee 仓库](https://img.shields.io/badge/Gitee-仓库-C71D23?logo=gitee)][RepositoryOnGitee]
[![GitHub 仓库](https://img.shields.io/badge/GitHub-仓库-0969da?logo=github)][RepositoryOnGithub]

**平台**：
[![Windows7+（exe）](https://img.shields.io/badge/Windows_7+-exe-0078D4?logo=windows)][ReleaseOnGitee]
[![Python3.12+（pyzw）](https://img.shields.io/badge/Python_3.12+-pyzw-3776AB?logo=python&logoColor=f5f5f5)][ReleaseOnGitee]

**语言**：
**中文** |
[English](./README.md) |
<small>期待您的翻译！</small>

_该应用程序目前仅支持中文。_

</div>

VCF 生成器，输入姓名与手机号则自动生成用于批量导入到通讯录内的 VCF 文件。

[![许可证](https://img.shields.io/github/license/HelloTool/VCFGeneratorLiteForTkinter?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](./LICENSE)
[![贡献者公约](https://img.shields.io/badge/贡献者公约-2.1-4baaaa.svg)](./docs/CODE_OF_CONDUCT.zh.md)
[![Test](https://github.com/HelloTool/VCFGeneratorLiteForTkinter/actions/workflows/test.yml/badge.svg)](https://github.com/HelloTool/VCFGeneratorLiteForTkinter/actions/workflows/test.yml)

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

### 环境要求

不同的应用包有一不同环境要求，您需要根据您的系统环境选择对应的应用包。

| 软件包类型    | 系统环境                | 架构要求 | 特别说明                           |
| ------------- | ----------------------- | -------- | ---------------------------------- |
| 安装器/便携包 | Windows 7+              | x86_64   | Windows 7 需补丁文件（见下方说明） |
| Zip 应用      | Python 3.12+ 与 Tkinter | 无限制   | -                                  |

### 获取软件包

通过以下渠道获取软件包：

- [Gitee 发行版][ReleaseOnGitee]
- [GitHub Releases][ReleaseOnGithub]

各系统对应文件清单：

| 软件包类型 | Windows               | Linux                   | macOS                   | Android |
| ---------- | --------------------- | ----------------------- | ----------------------- | ------- |
| 安装器     | `*_setup.exe`（推荐） | 暂未提供                | 暂未提供                | 不支持  |
| 便携包     | `*_portable.zip`      | 暂未提供                | 暂未提供                | 不支持  |
| Zip 应用   | `*_zipapp.pyzw`       | `*_zipapp.pyzw`（推荐） | `*_zipapp.pyzw`（推荐） | 不支持  |

## 使用方法

1. 把名字和电话以每行 `姓名 电话号码 备注` 的格式复制到下面的编辑框内，其中备注可忽略。
   ```text
   张三	13345367789	著名的法外狂徒
   李四	13445467890
   王五	13554678907
   赵六	13645436748
   ```
2. 点击“生成”，选择一个路径保存文件。
3. 将生成后的 VCF 文件复制到手机内，打开文件时选择使用“通讯录”，然后根据提示操作。
4. 等待导入完成。

> [!NOTE] 说明
>
> - 制表符会自动转换为空格处理，您可以同时使用制表符和空格分割。
> - 程序会自动去除输入框内多余的空格。
> - 如果每行有多个空格，则会将最后一个空格以前所有的字符当作姓名处理。
>
> 比如 `东坡居士 苏轼   13333333333  眉州眉山人` 将会被识别为
>
> > - 姓名：东坡居士 苏轼
> > - 电话：13333333333
> > - 备注：眉州眉山人
>

## 兼容性

### 应用兼容性

| 系统环境       | 特性     | 兼容性                                          |
| -------------- | -------- | ----------------------------------------------- |
| Windows 10+    | 深色模式 | 不支持深色模式                                  |
| Windows 10+    | 显示缩放 | 切换 DPI 时无法自动缩放，缩放适配由操作系统完成 |
| Windows 10+    | 字体缩放 | 不支持字体缩放                                  |
| Windows 7+     | 显示缩放 | 仅支持 100%、125%、150% 级别图标缩放            |
| Windows 7～8.1 | 应用启动 | 需要补丁                                        |

#### 特别说明

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

### vCard 文件兼容性

本 APP 仅支持生成仅包含姓名和电话的 2.1 版本 vCard 文件。

| 第三方应用     | 兼容性                      |
| -------------- | --------------------------- |
| Windows 联系人 | 非 UTF-8 环境下中文姓名乱码 |

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

请参见 [《开源声明》](./docs/legal/os_notices.md)

[RepositoryOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/
[RepositoryOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/
[ReleaseOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[ReleaseOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
[PythonWin7RepositoryOnGithub]: https://github.com/adang1345/PythonWin7
