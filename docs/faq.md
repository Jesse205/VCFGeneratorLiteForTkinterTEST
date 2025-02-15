# 问题与回答

## 为什么生成文件时会卡使 UI 卡顿？

因为 [GIL] 的存在，生成文件时会卡使 UI 卡顿，但是不影响使用。对于 ZipApp 版本，您可以使用无 GIL 的 Python 解释器解决这个问题。

GIL: https://docs.python.org/zh-cn/3.13/glossary.html#term-global-interpreter-lock
