# 视觉设计

遵循微软 [桌面应用程序的设计基础知识](https://learn.microsoft.com/zh-cn/windows/win32/uxguide/designprinciples)。

## 应用主题

应用主题应该跟随系统。

## 应用图标

应用图标遵循 [Windows 11 图标设计规范](https://learn.microsoft.com/zh-cn/windows/apps/design/style/iconography/overview)。

应用图标颜色选取自 [2014 Material Design 调色板](https://m2.material.io/design/color/the-color-system.html#tools-for-picking-colors)。

## 系统图标

系统图标应该跟随系统。如果无法跟随系统，则使用 Emoji 代替。

## 图标路径

| 路径                                                           | 尺寸（px）      | 备注                     |
| -------------------------------------------------------------- | --------------- | ------------------------ |
| `项目/assets/images/icon.svg`                                  | `512x512`       | 应用图标，用于文档展示   |
| `项目/src/vcf_generator_lite/resources/images/icon-[size].png` | `[size]x[size]` | 应用图标，用于应用内展示 |
