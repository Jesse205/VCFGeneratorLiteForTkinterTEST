from tkinter.font import nametofont


def extend_font_scale(origin_name: str, scale: float):
    font = nametofont(origin_name).copy()
    font.configure(size=round(int(font.actual("size")) * scale))
    return font
