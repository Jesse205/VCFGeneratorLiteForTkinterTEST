from tkinter import messagebox


def show_error(title="错误", *values: object):
    messagebox.showerror(title, " ".join(map(lambda value: str(value), values)))


def show_info(title="信息", *values: object):
    messagebox.showinfo(title, " ".join(map(lambda value: str(value), values)))