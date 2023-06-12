from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox


def write_file(file_path, content) -> bool:
    try:
        with open(file_path, "w", encoding='utf-8') as v:
            v.write(content)
            return True
    except OSError as err:
        print_error(str(err))
    return False


def generateFile():
    textContent = textInput.get(0.0, "end")
    vcfContent = generateContent(textContent)
    # print(vcfContent)
    file_path = "phones.vcf"
    write_state = write_file(file_path, vcfContent)
    if write_state:
        messagebox.showinfo("生成 VCF 文件完成", f"已导出文件到 \"{file_path}\"。")


def print_error(content: str):
    print(content)
    messagebox.showerror("错误", content)


def generateContent(textContent: str):
    content = ""
    textContent = textContent.replace("\t", " ")
    for lineText in textContent.split("\n"):
        lineText = lineText.strip()
        # 空行跳过
        if lineText == "":
            continue
        lineContent = lineText.rsplit(" ", 1)
        if len(lineContent) != 2:
            print_error(f"\"{lineText}\" 无法识别")
            continue
        name = lineContent[0].strip()
        phone = lineContent[1].strip()
        print(f"name = {name}, phone = {phone}")

        if not phone.isnumeric():
            print_error(f"\"{lineText}\" 电话号码不合法")
            continue
        content += f"""BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{str_to_hex(name)}
TEL;CELL:{phone}
END:VCARD

"""
    return content


def str_to_hex(str_to_chg):
    tmp_bytes = bytes(str_to_chg, encoding='utf-8')
    tmp_chars = []
    for each_byte in tmp_bytes:
        tmp_chars.append('=' + str(hex(int(each_byte))).replace('0x', '').upper())
    return ''.join(tmp_chars)


top = Tk()
top.title("VCF 生成器")
label = Label(top, text="""1. 把名字和电话以下面的格式复制到编辑框内
2. 点击“生成”，软件会创建名为“phones.vcf”的文件
3. 将“phones.vcf”复制到手机内，打开文件时选择使用“通讯录”，然后选择“确定”
4. 等待导入完成""", justify=LEFT)
label.pack(fill=X, padx=5, pady=5)
button = Button(top, text="生成", command=generateFile)
button.pack(padx=5, pady=5)

textInput = Text(top)
textInput.insert(0.0, """名字1	13345367789
名字2	13245467890
名字3	13154678907
名字4	13145436748
""")
textInput.pack(fill=BOTH, padx=5, pady=5)

top.mainloop()
