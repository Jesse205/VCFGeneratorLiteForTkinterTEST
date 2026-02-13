from tkinter import Text


def get_display_lines_fast(text: Text, index1: str, index2: str):
    """
    根据已显示位置与高度参数测量 *index1* 与 *index2* 之间的显示行数。

    可以一定程度上替代 ``Text#count(index1, index2, "displaylines", return_ints=True)``。
    """

    index1_dlineinfo = text.dlineinfo(index1)
    if index1_dlineinfo is None:
        return 1
    index2_dlineinfo = text.dlineinfo(index2)
    if index2_dlineinfo is None:
        return 1

    _, index1_y, _, index1_height, _ = index1_dlineinfo
    _, index2_y, _, index2_height, _ = index2_dlineinfo

    line_height = max(index1_height, index2_height)
    if line_height == 0:
        return 1

    return round((index2_y - index1_y) / line_height)
