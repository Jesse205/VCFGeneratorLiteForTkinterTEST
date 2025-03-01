# 应用配置指南

## 支持范围

- ✅ 支持类型：ZipApp 应用包
- ❌ 不支持类型：安装器、便携包

## 配置文件体系

### 文件位置

配置文件均位于用户主目录（`~`）

### 文件清单

| 文件名                    | 类型        | 作用域   | 备注                  |
| ------------------------- | ----------- | -------- | --------------------- |
| `.vcf_generator_lite.py`  | Python 配置 | 应用专用 | 可覆盖默认程序行为    |
| `.vcf_generator_lite.tcl` | TCL 配置    | 应用专用 | 优先于全局配置生效    |
| `.Tk.py`                  | Python 配置 | 全局配置 | 系统级 Python 配置    |
| `.Tk.tcl`                 | TCL 配置    | 全局配置 | 影响所有 Tkinter 应用 |

### 全局变量

| 变量名 | 作用                |
| ------ | ------------------- |
| `self` | 主窗口对象，Tk 实例 |

## 主题配置示例

### 切换 Clam 主题

1. 打开配置文件：`~/.vcf_generator_lite.py`
2. 添加配置代码：
    ```python
    from vcf_generator_lite.theme.clam_theme import ClamTheme

    self.set_theme(ClamTheme())
    ```

`ClamTheme` 会将 `clam` 主题应用到当前窗口，并覆盖一些默认样式，以便应用看起来更和谐。

### 创建 Classic 主题

1. 打开配置文件：`~/.vcf_generator_lite.py`
2. 添加配置代码：
    ````python
    from tkinter import Misc, Tk
    from tkinter.ttk import Style
    from typing import override

    from vcf_generator_lite.theme.base import BaseTheme


    class ClassicTheme(BaseTheme):
        @override
        def apply_theme(self, master: Misc, style: Style):
            super().apply_theme(master, style)
            style.theme_use("classic")
            style.configure("TButton", padding="1p", width=11)
            style.configure("Vertical.TScrollbar", arrowsize="9p")
            style.configure("InfoHeader.TFrame", relief="raised")
            style.configure("TextFrame.TEntry", padding=0, borderwidth="2p")

            window_background = style.lookup("TFrame", "background")
            if isinstance(master, Tk):
                master.configure(background=window_background)
            master.option_add("*Toplevel.background", window_background)


    self.set_theme(ClassicTheme())
    ```

在 `ClassicTheme` 中，首先应用了 `classic` 主题，然后覆盖了按钮、滚动条、关于对话框信息栏和输入框的样式，最后配置
`master` 窗口和接下来创建的任何 Toplevel 窗口的背景为主题背景。

## 最佳实践

1. 优先使用应用专用配置文件（`.vcf_generator_lite.py`）
2. 修改全局配置可能影响其他 Tkinter 应用
3. 配置生效需重启应用
