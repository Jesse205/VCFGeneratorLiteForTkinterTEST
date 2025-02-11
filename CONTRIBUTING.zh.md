# 贡献指南

本项目欢迎任何形式的贡献！

为了更好地理解开源贡献的流程，您可以参考《如何开源软件指南》中的“[为开源做贡献](https://opensource.guide/zh-hans/how-to-contribute/)”章节。此外，《开源指北》中的“[尝试参与开源](https://gitee.com/opensource-guide/guide/participating/roles.html)”章节也提供了详细的入门指导。

在提交贡献时，您需要遵守[贡献者公约](./CODE_OF_CONDUCT.zh.md)、各平台的规则以及当地法律法规。

## 翻译应用

敬请期待

## 提交反馈

您可以在 [Gitee issues][IssuesOnGitee] 或 [GitHub issues][IssuesOnGithub] 平台中提交反馈。

## 参与开发

1. 确保 [Gitee][RepositoryOnGitee] 或 [GitHub][RepositoryOnGithub] 中没有相关的 PR；
2. Fork 本项目；
3. 使用 [Git](https://git-scm.com/) 克隆项目到本地；
4. 创建分支，如 `feature/xxx` 或 `bugfix/xxx`；
5. 编写并提交代码；
6. 向本项目提交 Pull Request。

此外，有一些规范规则，请遵守：

## 图标规范

图标使用 Fluent 设计语言。

| 路径                                                    | 尺寸（px）      | 备注                                     |
| ------------------------------------------------------- | --------------- | ---------------------------------------- |
| `项目/docs/images/icon.png`                             | `512x512`       | 应用图标，用于文档展示                   |
| `项目/src/vcf_generator_lite/assets/images/icon.ico`    | `16x16-256x256` | 应用图标，需要附带 `256x256` 的 png 图片 |
| `项目/src/vcf_generator_lite/assets/images/icon-48.png` | `48x48`         | 应用图标，用于应用关于界面               |

## 代码规范

- Python（`.py`）：[PEP8](https://www.python.org/dev/peps/pep-0008/)；
- Markdown（`.md`）：[Markdownlint](https://github.com/DavidAnson/markdownlint)。
  - 本项目未完全遵守 Markdownlint 规范，详情请参考 [.markdownlint.json](./.markdownlint.json)。

详情请参考 [.editorconfig](./.editorconfig)。

## GIT 提交规范

遵循 Angular 的 [Commit Message Format](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format)。

### 类型

必须是以下之一：

- **build**：影响构建系统或外部依赖性的变化（示例范围：Gulp，Groccoli，NPM）
- **ci**：更改我们的 CI 配置文件和脚本（示例：Github Actions，SauceLabs）
- **docs**：仅更改文档
- **feat**：一个新功能
- **fix**：一个 bug 修复
- **perf**：改进的代码更改可改善性能
- **refactor**：代码更改既不修复错误也不添加功能
- **test**：添加丢失的测试或纠正现有测试

## UI 设计

使用平台样式，并且建议遵循微软[《桌面应用程序的设计基础知识》](https://learn.microsoft.com/zh-cn/windows/win32/uxguide/designprinciples)。

[RepositoryOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/
[RepositoryOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/
[IssuesOnGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/issues
[IssuesOnGithub]: https://github.com/HelloTool/VCFGeneratorLiteForTkinter/issues
