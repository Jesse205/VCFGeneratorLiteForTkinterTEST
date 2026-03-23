<div align="center">
<img src="./assets/images/icon.svg" width="192" height="192" alt="App icon" />

# VCF 生成器 Lite ![使用 Tkinter](https://img.shields.io/badge/使用-Tkinter-00319C)

**仓库**：
[![Gitee 主仓库](https://img.shields.io/badge/Gitee-主仓库-C71D23?logo=gitee)][repository-gitee]
[![GitHub 副仓库](https://img.shields.io/badge/GitHub-副仓库-0969da?logo=github)][repository-github]

**平台**：
[![Windows8.1+ (exe)](https://img.shields.io/badge/Windows_8.1+-exe-0078D4?logo=windows)][release-gitee]
[![Python3.12+ (pyzw)](https://img.shields.io/badge/Python_3.12+-pyzw-3776AB?logo=python&logoColor=f5f5f5)][release-gitee]

**语言**：
**简体中文** |
[English](./README.md) |
<small>期待您的翻译！</small>

</div>

VCF 生成器 Lite 可以将联系人列表转换为单个 vCard 文件，可批量导入到手机通讯录，或者用作其它用途。

[![许可证](https://img.shields.io/github/license/hellotool/VCFGeneratorLiteWithTkinter?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](./LICENSE)
[![贡献者公约](https://img.shields.io/badge/贡献者公约-2.1-4baaaa.svg)](./CODE_OF_CONDUCT.zh-CN.md)

[![Test](https://github.com/hellotool/VCFGeneratorLiteWithTkinter/actions/workflows/test.yml/badge.svg)](https://github.com/hellotool/VCFGeneratorLiteWithTkinter/actions/workflows/test.yml)

## 特性

- **智能解析**：按 `姓名 电话 备注` 格式批量识别联系人（备注可选），自动处理制表符和空格。
- **批量生成**：将所有联系人合并生成单个 `.vcf` 文件。
- **号码校验**：自动跳过无效号码，并快速定位错误行。
- **辅助编辑**：文本区显示行号，支持一键删除引号。

## 软件截图

<img src="./assets/images/screenshots/main_window.zh-CN.webp" width="451" alt="主窗口" />
<img src="./assets/images/screenshots/invalid_lines_window.zh-CN.webp" width="376" alt="错误行展示窗口" />

## 获取应用

### 下载软件包

您可以通过以下渠道下载软件包：

- [Gitee 发行版][release-gitee]
- [GitHub Releases][release-github]

请根据您的使用平台选择相应的软件包：

| 平台    | 软件包类型      | 需要安装 | 文件                                                       |
| ------- | --------------- | -------- | ---------------------------------------------------------- |
| Windows | 安装程序        | 是       | VCFGeneratorLite-\<应用版本\>-**win-amd64**-*setup.exe*    |
| Windows | 便携版          | 否       | VCFGeneratorLite-\<应用版本\>-**win-amd64**-*portable.zip* |
| 跨平台  | Python Wheel    | 可选     | vcf_generator_lite-\<应用版本\>-**py3-none-any**.*whl*     |
| 跨平台  | Python ZIP 应用 | 否       | VCFGeneratorLite-\<应用版本\>-**py3**.*pyzw*               |

### 使用 Python Wheel

您可以通过多种方式使用 Python Wheel 文件，以下介绍使用 [uv 工具][uv-homepage]的方法。

**安装到系统环境**：

```bash
uv tool install <whl 文件路径>
```

安装完成后，可通过以下命令运行：

```bash
uv tool run vcf-generator-lite
# 或
vcf-generator-lite
```

**直接运行（不安装）**：

```bash
uvx <whl 文件路径>
```

## 使用方法

1. 把名字和电话以每行 `姓名 电话 备注` 的格式复制到主界面的文本框中，其中备注可忽略。例如：
   ```text
   张三	13345367789	网络名人
   李四	13445467890
   王五	13554678907
   赵六	13645436748
   ```
2. 点击 **开始生成**，选择一个路径保存文件。
3. 您可以将生成后的 vCard 文件用在您需要的地方，详情请参阅下文 [使用 vCard 文件](#使用-vcard-文件)。

> [!NOTE]
>
> - 您可以同时使用制表符和空格分割姓名与电话号码。
> - 程序会自动去除文本框内多余的空格。
>
> 例如 `东坡居士 苏轼   13333333333  眉州眉山人` 将会被识别为
>
> > - 姓名：东坡居士 苏轼
> > - 电话：13333333333
> > - 备注：眉州眉山人
>

### 使用 vCard 文件

<details>
<summary>导入到手机通讯录</summary>

1. 传输 vCard 文件到手机内。
2. 打开 vCard 文件，选择 **通讯录**，然后根据提示操作。
3. 等待导入完成。

</details>

<details>
<summary>导入到 QQ 邮箱</summary>

1. 打开新版 QQ 邮箱网站。
2. 在侧边栏中选择 **应用 > 联系人**，然后选择 **管理 > 导入联系人**。
3. 在弹出的对话框中，点击 **选择文件** 选择框，选择您的 vCard 文件。
4. 点击 **开始导入**。

</details>

<details>
<summary>导入到飞书</summary>

1. 打开飞书客户端。
2. 在侧边栏中选择 **通讯录 > 邮箱通讯录**，然后选择 **添加 > 导入联系人** 按钮。
3. 在弹出的对话框中，选择或拖入您的 vCard 文件。
4. 点击 **导入**。

</details>

## 兼容性

### 系统要求

| 软件包类型               | 系统环境                        |
| ------------------------ | ------------------------------- |
| Windows 安装程序、便携版 | Windows 8.1 或更高版本          |
| Python ZIP 应用          | Python 3.12 或更高版本、Tkinter |

如果您想在 Windows 8 及以下版本中使用本应用，请参阅 [在旧版本 Windows 中运行](./docs/compatibility/runs-on-older-windows.md)。

在 Windows 中，如果您想直接双击启动 Python ZIP 应用，您需要安装 [Python 启动器][pylauncher] 或者 [Python 安装管理器][pymanager]。

### 功能兼容性

| 系统环境              | 特性     | 说明                                    |
| --------------------- | -------- | --------------------------------------- |
| Windows 10 或更高版本 | 深色模式 | 不支持深色模式                          |
| Windows 10 或更高版本 | 显示缩放 | 切换 DPI 时，由操作系统自动完成缩放适配 |

如果您想在 Windows 中使用深色模式，您可以[启用高对比度模式][windows-high-contrast-support]，或者使用 [Rectify11][rectify11] 等其他第三方工具修改系统主题。

### 文件兼容性

- **支持 vCard 版本**：2.1
- **支持字段**：姓名、电话号码、备注
- **已知问题**：
  - **Windows 联系人**：在非 UTF-8 环境下可能出现乱码。

## 致谢

- **AI 编码助手**：本项目部分代码、测试代码由 AI 编码助手辅助生成。
  - DeepSeek
  - 通义灵码
- **开源代码**：本项目使用了一些开源代码，详情请见 [开源声明](./docs/legal/os-notices.md)。

## 许可证

本项目以 Apache 2.0 许可证授权，详情请参阅 [LICENSE 文件](./LICENSE)。

```txt
Copyright 2023-2026 Jesse205

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

## 更多文档

- [开发指南](./docs/dev/index.md)
- [贡献指南](./CONTRIBUTING.md)
- [常见问题](./docs/faq.md)

[repository-gitee]: https://gitee.com/hellotool/VCFGeneratorLiteWithTkinter/
[repository-github]: https://github.com/hellotool/VCFGeneratorLiteWithTkinter/
[release-gitee]: https://gitee.com/hellotool/VCFGeneratorLiteWithTkinter/releases/latest
[release-github]: https://github.com/hellotool/VCFGeneratorLiteWithTkinter/releases/latest
[pylauncher]: https://docs.python.org/zh-cn/3.15/using/windows.html#python-launcher-for-windows-deprecated
[pymanager]: https://docs.python.org/zh-cn/3.15/using/windows.html#python-install-manager
[windows-high-contrast-support]: https://support.microsoft.com/zh-cn/windows/%E5%9C%A8-windows-%E4%B8%AD%E6%9B%B4%E6%94%B9%E9%A2%9C%E8%89%B2%E5%AF%B9%E6%AF%94%E5%BA%A6-fedc744c-90ac-69df-aed5-c8a90125e696
[rectify11]: https://www.rectify11.com/
[uv-homepage]: https://docs.astral.sh/uv/
