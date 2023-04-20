# VCF生成器 Lite

![许可证：MIT](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF%E8%AF%81-MIT-green)

VCF生成器，输入姓名与手机号则自动生成用于批量导入的VCF文件

## 使用方法

使用 Python 解析器运行 `vcf生成器.py` 或者运行发行版中 `启动vcf生成器.bat` 即可启动程序

1. 把名字和电话以下面的格式复制到编辑框内
2. 点击“生成”，软件会创建名为 `phones.vcf` 的文件
3. 将 `phones.vcf` 复制到手机内，打开文件时选择使用“通讯录”，然后选择“确定”
4. 等待导入完成

## 软件架构

无

## 构建

* 终端内执行 `python.exe -m PyInstaller vcf生成器.spec` 即可
* 或者直接运行 `build.bat`

