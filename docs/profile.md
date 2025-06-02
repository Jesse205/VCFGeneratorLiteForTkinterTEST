# 应用配置指南

通过修改配置文件，可自定义应用外观和功能。本应用基于 Tkinter 的 `readprofile` 机制实现配置管理，配置在重启后生效。

## 快速开始

1. 复制配置文件模板到 `~/.vcf_generator_lite.py`。
2. 根据[主题配置示例](#主题配置示例)添加代码。
3. 保存文件并重启应用生效。

## 支持范围

- **支持类型**：ZipApp 应用包
- **不支持类型**：安装器、便携包

## 配置文件

| 文件类型    | 文件名                      |
| ----------- | --------------------------- |
| Python 配置 | `~/.vcf_generator_lite.py`  |
|             | `~/.VCFGeneratorLite.py`    |
| Tcl 配置    | `~/.vcf_generator_lite.tcl` |
|             | `~/.VCFGeneratorLite.tcl`   |

## 全局变量

| 变量名 | 作用                  |
| ------ | --------------------- |
| `self` | 主窗口对象（Tk 实例） |

## 主题配置示例

<details>
<summary>切换 Clam 主题</summary>

1. 打开配置文件：`~/.vcf_generator_lite.py`
2. 添加配置代码：
    ```python
    from vcf_generator_lite.theme.clam_theme import ClamTheme

    self.set_theme(ClamTheme())
    ```

`ClamTheme` 会将 `clam` 主题应用到当前窗口，并覆盖一些默认样式，以便应用看起来更和谐。

</details>

<details>
<summary>创建 Classic 主题</summary>

1. 打开配置文件：`~/.vcf_generator_lite.py`
2. 添加配置代码：
    ````python
    from tkinter import Tk
    from tkinter.ttk import Style
    from typing import override

    from vcf_generator_lite.theme.base import BaseTheme


    class ClassicTheme(BaseTheme):
        @override
        def apply_tk(self, master: Tk, style: Style):
            super().apply_tk(master, style)
            style.theme_use("classic")
            style.configure("TButton", padding="1p", width=11)
            style.configure("Vertical.TScrollbar", arrowsize="9p")
            style.configure("DialogHeader.TFrame", relief="raised")
            style.configure("TextFrame.TEntry", padding=0, borderwidth="2p")

            window_background = style.lookup("TFrame", "background")
            master.configure(background=window_background)
            master.option_add("*Toplevel.background", window_background)


    self.set_theme(ClassicTheme())
    ```

在 `ClassicTheme` 中，首先应用了 `classic` 主题，然后覆盖了按钮、滚动条、关于对话框信息栏和输入框的样式，最后配置
`master` 窗口和接下来创建的任何 Toplevel 窗口的背景为主题背景。

</details>

### 组件样式

| 样式                         | 作用                              | 示例场景                     |
| ---------------------------- | --------------------------------- | ---------------------------- |
| `TLabel`                     | 标签样式                          | 主窗口介绍标签               |
| `TButton`                    | 按钮样式                          | 生成按钮                     |
| `TEntry`                     | 输入框样式                        | -                            |
| `TFrame`                     | 框架样式                          | 主窗口布局容器               |
| `TextFrame.TEntry`           | [`ttk-text`][ttk-text] 输入框样式 | 联系人输入框、关于窗口输入框 |
| `DialogHeader.TFrame`        | 对话框头部样式                    | 关于对话框标题栏             |
| `DialogHeaderContent.TFrame` | 对话框头部区域样式                | 关于对话框内容容器           |
| `DialogHeaderContent.TLabel` | 对话框头部标签样式                | 关于对话框版本信息显示       |

[ttk-text]: https://github.com/Jesse205/TtkText
