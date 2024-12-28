from tkinter import messagebox, Misc


def show_error(master=Misc, title="错误", *values: object):
    messagebox.showerror(title, " ".join(map(lambda value: str(value), values)), master=master)


def show_info(master=Misc, title="信息", *values: object):
    messagebox.showinfo(title, " ".join(map(lambda value: str(value), values)), master=master)


def show_warning(master=Misc, title="信息", *values: object):
    messagebox.showwarning(title, " ".join(map(lambda value: str(value), values)), master=master)
