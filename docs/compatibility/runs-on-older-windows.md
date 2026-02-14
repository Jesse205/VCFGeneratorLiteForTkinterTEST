# 在旧版本 Windows 中运行

> [!WARNING] 免责声明
>
> **请注意，我们强烈不推荐普通用户进行以下操作，并在此明确相关风险：**
>
> - **无官方支持**：开发团队**无法**为此类修改后的运行环境提供任何技术支持。若遇到问题，请自行解决。
> - **安全风险**：第三方补丁可能包含恶意代码、病毒或后门。您必须从**可信的来源**获取补丁，并在安装前**使用杀毒软件进行扫描**。我们对因使用第三方补丁而导致的任何安全漏洞或数据丢失**不承担责任**。
> - **稳定性风险**：修补后的环境可能发生崩溃、性能下降或兼容性问题。本应用在此类环境下**未经充分测试，无法保证稳定运行**。
> - **系统风险**：操作不当可能导致 Python 环境损坏或影响系统功能，届时可能需要重装 Python 或操作系统。
>
> **如果您选择继续，即表示您已充分了解并自愿承担所有相关风险。** 本项目的开发者及贡献者不对由此引发的任何直接或间接损失负责。

## 方案一：使用 [PythonWin7][pythonwin7_repository_github] ![Windows 7、Windows 8](https://img.shields.io/badge/Windows_7、Windows_8-0078D4)

**对于安装包、便携包用户：**

您需要使用 PythonWin7 内的文件替换本应用的文件。

1. **获取 Python 嵌入包**：从 [PythonWin7][pythonwin7_repository_github] 仓库下载：
   - `python-3.14.x-embed-amd64.zip`
2. **提取 DLL 文件**：解压下载的 ZIP 包，从中获取以下文件：
   - `python314.dll`
   - `api-ms-win-core-path-l1-1-0.dll`
3. **修补程序**：
   1. 对于安装程序类型：完成应用安装。
   2. 打开本软件目录下的 `_internal` 文件夹。
   3. 将下载的两个 DLL 文件覆盖到该目录。

**对于 Python ZIP 应用用户：**

您只需要安装 PythonWin7 提供的 Python。

1. **获取 Python 安装包**：从 [PythonWin7][pythonwin7_repository_github] 仓库下载：
   - 64 位系统：`python-3.14.x-amd64-full.exe`
   - 32 位系统：`python-3.14.x-full.exe`
2. **安装 Python**：运行安装程序，按照提示进行安装。

## 方案二：使用 VxKex NEXT 兼容层 ![Windows 7](https://img.shields.io/badge/Windows_7-0078D4)

**对于安装包、便携包用户：**

1. **安装 VxKex NEXT**：从 [VxKex NEXT Release][vxkex-next_release_github] 下载最新版本并安装。
2. **配置应用**：
   1. 打开 **VxKex NEXT 全局设置**（可在开始菜单中找到）。
   2. 将本软件目录下的 `vcf_generator_lite.exe` 添加到应用程序列表中。

**对于 Python ZIP 应用用户：**

1. **安装 VxKex NEXT**：从 [VxKex NEXT Release][vxkex-next_release_github] 下载最新版本并安装。
2. **安装 Python**：
   1. 打开 **VxKex NEXT 加载器**（可在开始菜单中找到）。
   2. 选择官方的 Python 安装程序路径，并在更多选项中勾选 **报告其他版本的 Windows**，并选择 Windows 10 或以上版本。
   3. 运行安装程序以完成 Python 安装。
3. **配置启动方式**：
   1. 将 Python 软件目录下的 `python.exe` 与 `pythonw.exe` 添加到 VxKex NEXT 的应用程序列表。
   2. 在 Python ZIP 应用的属性窗口中，将打开方式修改为 Python 软件目录中 `pythonw.exe`。

> [!NOTE]
>
> 您可能无法使用 Python 启动器来启动本应用，因为 Python 启动器找不到任何 Python 版本。

<!-- ## 方案三：使用 One-Core-API ![Windows XP](https://img.shields.io/badge/Windows_Server_2003、Windows_XP-0078D4)

该方法适用于 Windows Server 2003 RTM、SP1 和 SP2、Windows XP RTM、SP1、SP2 和 SP3 以及 Windows XP x64 SP1/SP2。 -->

[pythonwin7_repository_github]: https://github.com/adang1345/PythonWin7
[vxkex-next_release_github]: https://github.com/YuZhouRen86/VxKex-NEXT/releases/latest
