# 开发指南

本项目使用 Python 作为开发语言，使用 PDM 作为项目管理工具，使用 PyInstaller、ZipApp 作为打包工具，使用 InnoSetup 作为安装包生成工具。

## 开发准备

1. 安装 [Python 3.13+](https://www.python.org/)、[PDM](https://pdm-project.org/zh-cn/latest/)、[UPX](https://upx.github.io/)、[InnoSetup 6.4](https://jrsoftware.org/isinfo.php)；
2. 安装项目依赖：`pdm install`；
3. 安装 PDM 插件：`pdm install --plugins`；
4. 下载 InnoSetup 文件：`pdm run prepare_innosetup_extensions`。

## 构建应用

| 名称            | 命令                            |
| --------------- | ------------------------------- |
| 安装包（器）    | `pdm run build_app -t bundle`   |
| 便携式压缩文件  | `pdm run build_app -t portable` |
| Python Zip 应用 | `pdm run build_app -t zipapp`   |

## 项目结构

### 源代码

- `src`：源代码目录
  - `vcf_generator_lite/ui`： GUI 用户界面
  - `vcf_generator_lite/util`：工具类
  - `vcf_generator_lite/widget`：Tkinter 组件
  - `vcf_generator_lite/constants.py`：常量
  - `vcf_generator_lite/assets`：资源文件目录
  - `vcf_generator_lite/__main__.py`：程序入口
- `scripts`：脚本目录
- `pyproject.toml`：项目配置文件
- `setup.iss`：InnoSetup 配置文件，用于生成 Windows 安装器
- `vcf_generator_lite.spec`：PyInstaller 配置文件，用于构建 APP
- `metadata.yml`：信息文件（不包括版本），用于生成 versionfile.txt
- `versionfile.txt`：自动生成的信息文件，为 PyInstaller 提供 EXE 信息

## 常用命令

| 命令                       | 描述                 |
| -------------------------- | -------------------- |
| pdm run vcf-generator-lite | 运行应用             |
| pdm run build_app          | 构建应用             |
| pdm run version            | 显示或修改应用版本号 |

您可以通过 `pdm run --list` 查看所有自定义命令。
