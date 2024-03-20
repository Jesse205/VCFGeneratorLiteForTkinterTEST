def str_to_hex(content: str):
    tmp_bytes = bytes(content, encoding='utf-8')
    tmp_chars = []
    for each_byte in tmp_bytes:
        tmp_chars.append('=' + str(hex(int(each_byte))).replace('0x', '').upper())
    return ''.join(tmp_chars)


def get_vcard_item_content(name: str, phone: int):
    return f"""BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{str_to_hex(name)}
TEL;CELL:{phone}
END:VCARD"""
