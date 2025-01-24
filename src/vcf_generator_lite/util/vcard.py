import concurrent
import logging
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from queue import Queue
from typing import IO, Callable, Optional

from vcf_generator_lite.util.io import write_io_from_queue
from vcf_generator_lite.util.person import parse_person


@dataclass
class LineItem:
    line: int
    content: str


@dataclass
class GenerateResult:
    invalid_items: list[LineItem]
    exceptions: list[BaseException]


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


def generate_vcard_content(
    text_content: str,
    output_queue: Queue[str], *,
    on_total: Callable[[int], None] = None,
    on_item_invalid: Callable[[LineItem], None] = None
):
    # 将制表符转换为空格，统一处理
    text_content = text_content.replace("\t", " ")

    # 分割为列表并去除空格和空行
    items = [line_text.strip() for line_text in text_content.strip().split("\n") if line_text.strip() != ""]
    on_total(len(items))
    for position, line_text in enumerate(items, start=1):
        try:
            person = parse_person(line_text)
        except ValueError as e:
            logging.error(e)
            on_item_invalid(LineItem(position, line_text))
        else:
            output_queue.put(f"{get_vcard_item_content(person.name, person.phone)}\n\n")


def generate_vcard_file(
    input_text: str,
    output_io: IO,
    *,
    on_update_progress: Callable[[float, bool], None] = None,
):
    task_total_items_count = 0
    task_written_items_count = 0
    previous_progress: Optional[float] = None
    previous_determinate: Optional[bool] = None
    invalid_items: list[LineItem] = []
    exceptions: list[BaseException] = []
    write_queue = Queue()

    def update_progress():
        nonlocal previous_progress, previous_determinate
        if task_written_items_count > 0 and task_total_items_count > 0:
            progress = round(task_written_items_count / task_total_items_count, 1)
            determinate = True
        else:
            progress = -1.0
            determinate = False
        if progress != previous_progress or determinate != previous_determinate:
            previous_progress = progress
            previous_determinate = determinate
            on_update_progress(progress, determinate)

    def on_total(total: int):
        nonlocal task_total_items_count
        task_total_items_count = total
        update_progress()

    def on_item_finished():
        nonlocal task_written_items_count
        task_written_items_count += 1
        update_progress()

    def on_item_invalid(item: LineItem):
        invalid_items.append(item)
        on_item_finished()

    def on_write():
        on_item_finished()

    with ThreadPoolExecutor(max_workers=2) as executor:
        process_future: Future[GenerateResult] = executor.submit(
            generate_vcard_content,
            input_text,
            write_queue,
            on_total=on_total,
            on_item_invalid=on_item_invalid
        )
        process_future.add_done_callback(lambda _: write_queue.shutdown())
        write_future: Future[None] = executor.submit(
            write_io_from_queue,
            output_io,
            write_queue,
            on_write=on_write
        )
        result = concurrent.futures.wait([process_future, write_future],
                                         return_when=concurrent.futures.FIRST_EXCEPTION)

        for future in result.done:
            if (exception := future.exception()) is not None:
                exceptions.append(exception)

    return GenerateResult(
        invalid_items=invalid_items,
        exceptions=exceptions
    )
