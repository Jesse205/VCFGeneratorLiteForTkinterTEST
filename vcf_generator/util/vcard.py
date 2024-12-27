import logging
from queue import Queue
from typing import IO, Callable

from vcf_generator.util.io import write_io_from_queue
from vcf_generator.util.person import parse_person
from vcf_generator.util.thread import io_executor


def _str_to_hex(content: str):
    tmp_bytes = bytes(content, encoding='utf-8')
    tmp_chars = []
    for each_byte in tmp_bytes:
        tmp_chars.append('=' + str(hex(int(each_byte))).replace('0x', '').upper())
    return ''.join(tmp_chars)


def get_vcard_item_content(name: str, phone: int):
    return f"""BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{_str_to_hex(name)}
TEL;CELL:{phone}
END:VCARD"""


class LineContent:
    def __init__(self, line: int, content: str):
        self.line = line
        self.content = content


class GenerateResult:

    def __init__(self, invalid_items: list[LineContent]):
        self.invalid_items = invalid_items


def generate_vcard_file(output_io: IO, text_content: str, on_update_progress: Callable[[float], None] = None):
    invalid_items: list[LineContent] = []

    # 将制表符转换为空格，统一处理
    text_content = text_content.replace("\t", " ")

    # 分割为列表并去除空格和空行
    items = [line_text.strip() for line_text in text_content.strip().split("\n") if line_text.strip() != ""]
    total = len(items)
    previous_progress = 0.0

    def on_write(written_count: int):
        nonlocal previous_progress
        progress = round(written_count / total, 1)
        if progress != previous_progress:
            previous_progress = progress
            on_update_progress(progress)

    io_queue: Queue[str] = Queue()
    io_executor.submit(write_io_from_queue, output_io, io_queue, on_write=on_write)

    for position, line_text in enumerate(items, start=1):
        try:
            person = parse_person(line_text)
        except ValueError as e:
            logging.error(e)
            invalid_items.append(LineContent(position, line_text))
        else:
            io_queue.put(f"{get_vcard_item_content(person.name, person.phone)}\n\n")

    io_queue.join()
    io_queue.shutdown()
    return GenerateResult(invalid_items)
