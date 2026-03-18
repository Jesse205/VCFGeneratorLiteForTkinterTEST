# 开发指南

## 技术栈

- **IDE**: [Visual Studio Code](https://code.visualstudio.com/) 或者 [PyCharm 2025.3.1](https://www.jetbrains.com/zh-cn/pycharm/)
- **开发语言**: [Python 3.12+][python-homepage]
- **UI 框架**: [Tkinter][tkinter-homepage]
- **包管理工具**: [uv][uv-homepage]
- **测试工具**: [pytest](https://docs.pytest.org/en/7.4.x/)
- **格式化工具**: [Ruff][ruff-formatter-homepage]
- **代码检查工具**: [Ruff][ruff-linter-homepage]、[Pyright][pyright-homepage]
- **构建工具**:
  - Windows: [PyInstaller](https://pyinstaller.org/en/stable/)、[InnoSetup 6.6+][innosetup-homepage]、[UPX](https://upx.github.io/)
  - ZIP 应用：[zipapp](https://docs.python.org/zh-cn/3/library/zipapp.html)

## 🛠️ 开发准备

### 环境配置

1. **安装基础工具**：
   - 下载并安装 Python 3.12+ 和 Tkinter
   - [安装 uv][uv-installation]
   - （可选）安装 UPX
   - 安装 InnoSetup（仅 Windows）
2. **安装依赖项**：
   ```bash
   uv sync
   ```

## 📦 构建应用

| 软件包类型       | 命令                                       |
| ---------------- | ------------------------------------------ |
| Windows 安装程序 | `uv run scripts/build_app.py -t innosetup` |
| 便携包           | `uv run scripts/build_app.py -t portable`  |
| Python ZIP 应用  | `uv run scripts/build_app.py -t zipapp`    |
| Python Wheel     | `uv build --wheel`                         |

## 项目结构

```txt
VCFGeneratorLiteWithTkinter/
├── scripts/                        # 构建脚本
├── src/                            # 源代码
│   └── vcf_generator_lite/
│       ├── core/                   # 业务逻辑
│       ├── resources/              # 静态资源（图标、数据等）
│       ├── themes/                 # 应用主题
│       ├── utils/                  # 工具类
│       ├── widgets/                # 自定义组件（增强型输入框等）
│       ├── windows/                # 窗口
│       ├── __main__.py             # 程序入口
│       └── constants.py            # 全局常量（名称、链接等）
├── pyproject.toml                  # 项目配置
├── vcf_generator_lite.iss          # InnoSetup 安装脚本
├── vcf_generator_lite.spec         # PyInstaller 配置
└── os_notices.toml                 # 开源声明信息
```

## 常用命令

| 命令                                 | 描述                           |
| ------------------------------------ | ------------------------------ |
| `uv run vcf-generator-lite`          | 运行应用                       |
| `uv run pytest`                      | 测试应用                       |
| `uv run ruff format`                 | 格式化所有代码                 |
| `uv run ruff check`                  | 检查所有代码                   |
| `uv run scripts/build_app.py`        | 构建应用                       |
| `uv version`                         | 查看当前版本                   |
| `uv version 1.2.3`                   | 更新版本号为 `1.2.3`           |
| `uv version --bump patch --bump dev` | 更新补丁版本，并更新为开发版本 |
| `uv version --bump stable`           | 更新为稳定版本                 |

## 🎨 UI 开发规范

### 单位系统

- **设计单位**：使用字体单位点 (`p`)，是[有效像素 (epx)](https://learn.microsoft.com/zh-cn/windows/apps/design/layout/screen-sizes-and-breakpoints-for-responsive-design#effective-pixels-and-scale-factor) 的 **0.75** 倍；
  - `7p` 为 `9.333epx`
  - `9p` 为 `12epx`
  - `12p` 为 `16epx`
- **布局原则**：
  - 尽量使用 `pack` 布局管理器，创建响应式 UI；
  - 组件间距统一使用 `padx=7p, pady=7p`。

## 版本

版本命名遵循 [Python 包版本规范][python-packaging-version-specifiers]。

### Windows 版本号映射

Windows 可执行文件的 `FixedFileInfo` 中的文件版本和产品版本仅支持四个 16 位整数（格式为 `A.B.C.D`）。为保留应用版本的详细信息，采用以下映射规则：

- **A.B.C** 直接对应应用版本的 `major.minor.micro`。
- **D（构建号）** 根据版本的预发布、开发、后发布状态计算得出。

构建号的计算公式如下：

```txt
D = 基础偏移 + 预发布号 × 100 + 后发布号 × 10 + （开发号 或 9）
```

- **基础偏移**：
  - Alpha 版本：`10000`
  - Beta 版本：`20000`
  - RC 版本：`30000`
  - 正式版本：`40000`
- **预发布号**：如果版本包含预发布标识（如 `a1`、`b2`、`rc3`），则取其中的数字；若无预发布标识，则视为 `0`。
- **后发布号**：如果版本包含后发布标识（如 `post1`），则取其中的数字；否则为 `0`。
- **开发号**：如果版本包含开发标识（如 `dev2`），则取其中的数字，此时**不加 9**；否则，在最后一项加 `9` 以表示非开发版本。

#### 示例

| 应用版本             | FixedFileInfo 版本 | 计算过程                 |
| -------------------- | ------------------ | ------------------------ |
| `1.2.3.dev1`         | `1.2.3.00001`      | 基础偏移 0 + 0 + 0 + 1   |
| `1.2.3a`             | `1.2.3.10009`      | 10000 + 0 + 0 + 9        |
| `1.2.3a1.dev2`       | `1.2.3.10102`      | 10000 + 1×100 + 0 + 2    |
| `1.2.3a1`            | `1.2.3.10109`      | 10000 + 1×100 + 0 + 9    |
| `1.2.3a1.post2.dev3` | `1.2.3.10123`      | 10000 + 1×100 + 2×10 + 3 |
| `1.2.3a1.post2`      | `1.2.3.10129`      | 10000 + 1×100 + 2×10 + 9 |
| `1.2.3b1`            | `1.2.3.20109`      | 20000 + 1×100 + 0 + 9    |
| `1.2.3rc1`           | `1.2.3.30109`      | 30000 + 1×100 + 0 + 9    |
| `1.2.3`              | `1.2.3.40009`      | 40000 + 0 + 0 + 9        |
| `1.2.3.post1.dev2`   | `1.2.3.40012`      | 40000 + 0 + 1×10 + 2     |
| `1.2.3.post1`        | `1.2.3.40019`      | 40000 + 0 + 1×10 + 9     |

[python-homepage]: https://www.python.org/
[uv-homepage]: https://docs.astral.sh/uv/
[uv-installation]: https://docs.astral.sh/uv/getting-started/installation/
[tkinter-homepage]: https://docs.python.org/zh-cn/3/library/tk.html
[ruff-formatter-homepage]: https://docs.astral.sh/ruff/formatter/
[ruff-linter-homepage]: https://docs.astral.sh/ruff/linter/
[innosetup-homepage]: https://jrsoftware.org/isinfo.php
[pyright-homepage]: https://microsoft.github.io/pyright
[python-packaging-version-specifiers]: https://packaging.python.org/en/latest/specifications/version-specifiers/
