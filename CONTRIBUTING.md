# 贡献指南

本项目欢迎任何形式的贡献！

如果您不了解如何参与开源贡献，您可以参考以下资源：

- GitHub 社区的 [开源软件指南][how-to-contribute-github-opensource-guide]
- Gitee 社区的 [开源指北][participating-gitee-opensource-guide]

在提交贡献时，您需要遵守 [贡献者公约](./CODE_OF_CONDUCT.zh-CN.md)、当前平台的规则以及当地法律法规。

## 本地化应用

本地化分为 *功能本地化* 和 *语言本地化* 两部分。

### 功能本地化

当前应用仅支持识别 11 位中国大陆手机号，暂不支持其他类型的号码。如果同时支持识别多种号码可能造成不可预料的结果。

### 语言本地化

若想为应用添加新的语言支持，请按以下步骤操作：

1. 定位到 `src/vcf_generator_lite/resources/locales` 目录。
2. 创建一个新的语言文件，格式为 `<语言代码>[_区域代码].toml`（例如：`es.toml` 或 `pt_BR.toml`）。
3. 参照已有的 `en.toml`（英文）或 `zh_CN.toml`（简体中文）文件的结构和键名，翻译对应的值。

## 提交反馈

如果您在使用中遇到问题或有改进建议，欢迎通过以下任一渠道提交反馈：

- [Gitee Issues][issues-gitee]
- [GitHub Issues][issues-github]

## 参与开发

1. 确保 [Gitee][repository-gitee] 或 [GitHub][repository-github] 中没有相关的拉取请求（PR）。
2. Fork 本仓库。
3. 使用 [Git][git-homepage] 克隆仓库到本地。
4. 阅读[开发指南](./docs/dev/index.md)，熟悉项目开发方法。
5. 创建分支，如 `feature/xxx` 或 `bugfix/xxx`。
6. 编写并提交代码。
7. 向本仓库提交 PR。

此外，有一些规范规则，请遵守：

## 代码规范

**Python (`.py`)：**

- 函数参数必须声明类型
- 单行最大 120 字符
- 其他情况以 [PEP8][pep-0008] 为准

**Markdown (`.md`)：**

- 不限制单行最大字符数
- 详情请参考 `.markdownlint.json`
- 其他情况以 [Markdownlint][markdownlint-repository-github] 为准

详情请参考 `.editorconfig`。

## 文档规范

遵守 [中文技术文档写作风格指南][zh-style-guide]。

## Git 提交规范

遵循 [约定式提交][conventionalcommits-homepage]。

## 视觉设计

详见 [视觉设计](./docs/dev/visual.md)

[repository-gitee]: https://gitee.com/hellotool/VCFGeneratorLiteWithTkinter/
[repository-github]: https://github.com/hellotool/VCFGeneratorLiteWithTkinter/
[issues-gitee]: https://gitee.com/hellotool/VCFGeneratorLiteWithTkinter/issues
[issues-github]: https://github.com/hellotool/VCFGeneratorLiteWithTkinter/issues

[markdownlint-repository-github]: https://github.com/hellotool/VCFGeneratorLiteWithTkinter/
[git-homepage]: https://git-scm.com/
[conventionalcommits-homepage]: https://www.conventionalcommits.org/zh-hans/v1.0.0/

[how-to-contribute-github-opensource-guide]: https://opensource.guide/zh-hans/how-to-contribute/
[participating-gitee-opensource-guide]: https://gitee.com/opensource-guide/guide/participating/roles.html
[zh-style-guide]: https://zh-style-guide.readthedocs.io/zh-cn/latest/index.html

[pep-0008]: https://peps.python.org/pep-0008/
