from tkinter import Text


def get_display_lines_fast(text: Text, index1: str, index2: str):
    """根据已显示位置与高度参数测量 *index1* 与 *index2* 之间的显示行数。

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


def select_text(text: Text, first: str, last: str, *, see: bool = True):
    text.tag_remove("sel", "1.0", "end")
    text.tag_add("sel", first, last)
    text.mark_set("insert", last)
    if see:
        text.see("insert")


def select_lines(text: Text, first_row: int, last_row: int, *, see: bool = True):
    select_text(text, f"{first_row}.0", f"{last_row + 1}.0", see=see)


def search_line(text: Text, search_text: str, near_row: int, max_offset: int = 20, *, strip: bool = True) -> int | None:
    """在 ``near_row`` 周围搜索整行，仅当 ``search_text`` 完全匹配该行时返回行号。

    为了防止数据过大时卡顿，默认会限制最大 20 的搜索范围。

    :return: 行号，未找到时返回 ``None``
    :rtype: int | None
    """
    if strip:
        search_text = search_text.strip()

    line_count = int(text.index("end").split(".")[0]) - 1
    for offset in range(min(max(line_count - near_row, near_row) + 1, max_offset)):
        top_row = near_row - offset
        bottom_row = near_row + offset

        if top_row > 0:
            top_line_text = text.get(f"{top_row}.0", f"{top_row}.end")
            if search_text == top_line_text.strip():
                return top_row

        if bottom_row <= line_count:
            bottom_line_text = text.get(f"{bottom_row}.0", f"{bottom_row}.end")
            if search_text == bottom_line_text.strip():
                return bottom_row
    return None
