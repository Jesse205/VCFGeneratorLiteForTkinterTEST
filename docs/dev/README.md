# 开发指南

## 技术栈

- **IDE**: [Visual Studio Code](https://code.visualstudio.com/) 或者 [PyCharm](https://www.jetbrains.com/zh-cn/pycharm/)
- **开发语言**: [Python 3.12+][PythonHomepage]
- **UI 框架**: [Tkinter](https://docs.python.org/zh-cn/3/library/tk.html)
- **包管理**: [PDM][PDMHomepage]
- **测试工具**: [pytest](https://docs.pytest.org/en/7.4.x/)
- **检查工具**: [Black](https://black.readthedocs.io/)
- **构建工具**: [PyInstaller](https://pyinstaller.org/en/stable/)、[ZipApp](https://docs.python.org/zh-cn/3/library/zipapp.html)、[InnoSetup 6.4+](https://jrsoftware.org/isinfo.php)、[UPX](https://upx.github.io/)

## 🛠️ 开发准备

### 环境配置

1. **安装基础工具**：
   - 下载并安装 Python 3.13+（勾选 `Add to PATH`）
   - [安装 PDM](https://pdm-project.org/zh-cn/latest/#_3)（包管理工具）
      ```bash
      pip install --user pdm
      ```
   - 安装 UPX（可选）
   - 安装 InnoSetup（仅 Windows）
2. **安装依赖项**：
   ```bash
   pdm install -G:all # 安装项目依赖
   pdm install --plugins  # 安装 PDM 插件
   pdm run prepare_innosetup_extensions  # 下载 InnoSetup 文件
   ```

## 📦 构建应用

| 应用包类型 | 命令                             |
| ---------- | -------------------------------- |
| 安装器     | `pdm run build_app -t installer` |
| 便携版     | `pdm run build_app -t portable`  |
| ZipApp     | `pdm run build_app -t zipapp`    |

## 项目结构

```txt
VCFGeneratorLiteForTkinter/
├── src/                          # 源代码
│   └── vcf_generator_lite/
│       ├── windows/              # 窗口
│       ├── utils/                # 工具类
│       ├── widgets/              # 自定义组件（增强型输入框等）
│       ├── themes/               # 应用主题
│       ├── resources/            # 静态资源（图标、数据等）
│       ├── services/             # 业务逻辑
│       ├── __main__.py           # 程序入口
│       └── constants.py          # 全局常量（名称、链接等）
├── scripts/                      # 构建脚本
├── pyproject.toml                # 项目配置
├── vcf_generator_lite.spec       # PyInstaller 配置
├── setup.iss                     # InnoSetup 安装脚本
├── metadata.yml                  # 元数据（作者、描述等）
├── versionfile.txt               # 版本信息（自动生成）
└── os_notices.toml               # 开源声明信息
```

## 常用命令

| 命令                         | 描述                                    |
| ---------------------------- | --------------------------------------- |
| `pdm run vcf-generator-lite` | 运行应用                                |
| `pdm run build_app`          | 构建应用                                |
| `pdm run version`            | 查看当前版本                            |
| `pdm run version 1.2.3`      | 更新版本号为 `1.2.3` 并同步所有配置文件 |

您可以通过 `pdm run --list` 查看所有自定义命令。

## 🎨 UI 开发规范

### 单位系统

- **设计单位**：使用字体单位点 (`p`)，是[有效像素 (epx)](https://learn.microsoft.com/zh-cn/windows/apps/design/layout/screen-sizes-and-breakpoints-for-responsive-design#effective-pixels-and-scale-factor) 的 **0.75** 倍；
   ```python
   # 转换示例：9p 在 100% 缩放中表示为 12px
   Label(root, text="示例", font=("微软雅黑", 9))  # 默认9p字体
   ```
- **布局原则**：
   - 尽量使用 `pack` 布局管理器，创建响应式 UI；
   - 组件间距统一使用 `padx=7p, pady=7p`。

[PythonHomepage]: https://www.python.org/
[PDMHomepage]: https://pdm-project.org/
[TkinterHomepage]: https://docs.python.org/zh-cn/3/library/tk.html
