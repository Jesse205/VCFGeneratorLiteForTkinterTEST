# 贡献指南

## 图标生成

1. 制作大小为 `512x512` 的图标，重命名为 `icon.png`；
2. 使用 [FreeConvert](https://www.freeconvert.com/zh/ico-converter) 生成`.ico`文件，命名为 `icon.ico`；
3. 生成 `48x48` 的图标，重命名为 `icon-48.png`；
4. 将这些图标放入 [/vcf_generator/assets](/vcf_generator/assets) 目录中。

## 代码规范

- Python（`.py`）：[PEP8](https://www.python.org/dev/peps/pep-0008/)；
- Markdown（`.md`）：[Markdownlint](https://github.com/DavidAnson/markdownlint)。

详情请参考 [.editorconfig](./.editorconfig)。

## GIT 提交规范

参考 Angular 的 [Commit Message Format](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format)。

## UI 设计

使用平台样式，并且建议遵循微软[《桌面应用程序的设计基础知识》](https://learn.microsoft.com/zh-cn/windows/win32/uxguide/designprinciples)。

注意事项：

- 代码中布局尺寸单位是点（`p`），而不是像素 (`px`) 、[有效像素 (`epx`) ](https://learn.microsoft.com/zh-cn/windows/apps/design/layout/screen-sizes-and-breakpoints-for-responsive-design#effective-pixels-and-scale-factor)；
- 本软件的点（`p`）单位与 Tkinter 默认的点（`p`）单位不同，本软件的点（`p`）与有效像素 (`epx`)相同；
- 由于字体单位也使用点（`p`），因此在本软件中，字体的单位与有效像素 (`epx`)相同，与 Tkinter 默认的点（`p`）单位不同。
