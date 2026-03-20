import binascii
import logging
import queue
import time
from collections.abc import Callable
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from dataclasses import dataclass
from threading import RLock, Thread
from typing import IO, NamedTuple, override

from vcf_generator_lite.models.contact import Contact, PhoneNotFoundError, parse_contact
from vcf_generator_lite.models.phone_rule import PhoneRule
from vcf_generator_lite.utils.deque_queue import DequeQueue

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InvalidItem:
    row_position: int
    raw_content: str
    exception: BaseException


@dataclass(frozen=True)
class GenerateResult:
    invalid_items: list[InvalidItem]
    exception: BaseException | None
    time_elapsed: float
    saved_count: int


class _WriteQueueItem(NamedTuple):
    row_position: int
    raw_content: str
    vcard: str


def utf8_to_qp(text: str) -> str:
    return binascii.b2a_qp(text.encode("utf-8")).decode("utf-8")


def serialize_to_vcard(contact: Contact):
    items: list[str | None] = [
        "BEGIN:VCARD",
        "VERSION:2.1",
        f"FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{utf8_to_qp(contact.name)}" if contact.name else None,
        f"TEL;CELL:{contact.phone}",
        f"NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{utf8_to_qp(contact.note)}" if contact.note else None,
        "END:VCARD",
    ]
    filtered_items = (item for item in items if item is not None)
    return "\n".join(filtered_items)


class VCFGeneratorTask(Thread):
    def __init__(
        self,
        input_text: str,
        output_io: IO[str],
        progress_listener: Callable[[float, bool], None] | None = None,
        result_listener: Callable[[GenerateResult], None] | None = None,
        phone_rules: list[PhoneRule] | None = None,
    ):
        super().__init__()
        self._progress_listener = progress_listener
        self._result_listener = result_listener
        self._input_text = input_text
        self._output_io = output_io
        self._phone_rules = phone_rules

        self._total: int = 0
        self._processed: int = 0
        self._progress: float = 0
        self._saved_count: int = 0

        self._invalid_items: list[InvalidItem] = []

        self._total_lock = RLock()
        self._processed_lock = RLock()
        self._progress_lock = RLock()
        self._saved_count_lock = RLock()

        self.__stopping: bool = False
        # 使用 deque 会比原生的 queue 性能高
        self._write_queue: DequeQueue[_WriteQueueItem | None] = DequeQueue(10)
        self.result: GenerateResult | None = None

    @property
    def is_stopping(self) -> bool:
        return self.__stopping

    def stop(self):
        self.__stopping = True
        self._write_queue.shutdown()

    @override
    def run(self):
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="VCFGenerator") as pipeline_executor:
            write_future = pipeline_executor.submit(self._write_output)
            parse_future = pipeline_executor.submit(self._parse_input)
            done, _ = wait([parse_future, write_future], return_when=FIRST_EXCEPTION)
        end_time = time.time()

        self._write_queue.shutdown()

        exception: BaseException | None = None
        for future in done:
            if (future_exception := future.exception()) and not isinstance(future_exception, queue.ShutDown):
                exception = future_exception
                break

        self.result = GenerateResult(
            invalid_items=self._invalid_items,
            exception=exception,
            time_elapsed=end_time - start_time,
            saved_count=self._saved_count,
        )
        if self._result_listener:
            self._result_listener(self.result)

    def _parse_input(self) -> None:
        lines = self._input_text.strip().split("\n")
        self._total = len(lines)
        self._notify_progress()
        for position, line in enumerate((line.strip() for line in lines), 1):
            if self.__stopping:
                break
            if not line:
                self._skip_item()
                continue

            queue_item: _WriteQueueItem | None = None
            try:
                contact = parse_contact(contact_text=line, rules=self._phone_rules)
                vcard = serialize_to_vcard(contact)
                queue_item = _WriteQueueItem(row_position=position, raw_content=line, vcard=vcard)
            except PhoneNotFoundError as e:
                _logger.warning(f"Phone not found at line {position}: {e}")

                # list 的 append 方法是原子的，因此不需要加锁
                # https://docs.python.org/zh-cn/3/library/threadsafety.html#thread-safety-list
                self._invalid_items.append(InvalidItem(row_position=position, raw_content=line, exception=e))
            except Exception as e:
                _logger.warning(f"Parsing error at line {position}", exc_info=e)
                self._invalid_items.append(InvalidItem(row_position=position, raw_content=line, exception=e))

            if queue_item:
                self._write_queue.put(queue_item)
            else:
                self._finish_item(success=False)

        self._write_queue.put(None)  # 结束信号

    def _write_output(self):
        while (item := self._write_queue.get()) is not None:
            try:
                self._output_io.write(item.vcard)
                self._output_io.write("\n\n")
            except BaseException:
                self._finish_item(success=False)
            else:
                self._finish_item(success=True)

    def _notify_progress(self):
        if self._progress_listener is None:
            return
        self._progress_listener(self._progress, self._total > 0)

    def _update_progress(self):
        if self._total == 0:
            return
        new_progress = round(min(self._processed / self._total, 1.0), 1)
        if self._progress != new_progress:
            with self._progress_lock:
                if self._progress != new_progress:
                    self._progress = new_progress
                    self._notify_progress()

    def _skip_item(self):
        with self._total_lock:
            self._total -= 1
        self._update_progress()

    def _finish_item(self, success: bool = True):
        with self._processed_lock:
            self._processed += 1
        if success:
            with self._saved_count_lock:
                self._saved_count += 1
        self._update_progress()
