# 常见问题

## 为什么生成文件时界面卡顿？

生成文件时界面卡顿主要是由于 Python 的 [全局解释器锁（GIL）][gil]机制，它限制同一时刻只能有一个线程执行字节码，从而在多线程场景下影响性能。

如果您在使用 ZIP 应用时遇到界面卡顿的问题，以考虑使用支持自由线程的 Python 解释器来运行您的应用，这样可以避免 GIL 带来的限制，从而提升多线程应用的性能。

有关自由线程的更多信息，请参阅 [自由线程的 CPython][free-threaded-cpython]。

[gil]: https://docs.python.org/zh-cn/3.13/glossary.html#term-global-interpreter-lock
[free-threaded-cpython]: https://docs.python.org/zh-cn/3.14/whatsnew/3.13.html#whatsnew313-free-threaded-cpython

## 为什么提示“缺失号码或号码不正确”？

目前软件只支持识别 11 位中国大陆手机号。

如果输入的不是这种号码（比如固话、短号、其他国家手机号），就会提示“缺失号码或号码不正确”。

后续可能会扩展支持更多号码类型，敬请关注更新。
