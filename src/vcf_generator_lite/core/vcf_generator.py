import binascii
import logging
import time
from collections.abc import Callable
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from threading import Lock, RLock, Thread
from typing import IO, NamedTuple, override

from vcf_generator_lite.models.contact import Contact, PhoneNotFoundError, parse_contact
from vcf_generator_lite.utils.deque_queue import DequeQueue

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InvalidLine:
    row_position: int
    content: str
    exception: BaseException


@dataclass
class VCardGeneratorState:
    total: int = 0
    processed: int = 0
    progress: float = 0
    invalid_lines: list[InvalidLine] = field(default_factory=list)
    running: bool = False
    start_time: float = 0.0


@dataclass(frozen=True)
class GenerateResult:
    invalid_lines: list[InvalidLine]
    exception: BaseException | None
    time_elapsed: float
    total: int


class WriteQueueItem(NamedTuple):
    row_position: int
    origin_content: str
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
    ):
        super().__init__()
        self._progress_listener = progress_listener
        self._result_listener = result_listener
        self._input_text = input_text
        self._output_io = output_io
        self._state = VCardGeneratorState()
        self._count_lock = RLock()
        self._processed_lock = RLock()
        self._progress_lock = RLock()
        self._lock = Lock()
        # 使用 deque 会比原生的 queue 性能高
        self._write_queue: DequeQueue[WriteQueueItem | None] = DequeQueue(10)
        self.result: GenerateResult | None = None

    @override
    def run(self):
        self._state.running = True
        self._state.start_time = time.time()
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="VCFGenerator") as pipeline_executor:
            write_future = pipeline_executor.submit(self._write_output)
            parse_future = pipeline_executor.submit(self._parse_input)
            done, _ = wait([parse_future, write_future], return_when=FIRST_EXCEPTION)
        end_time = time.time()
        self._state.running = False

        exception: BaseException | None = None
        for future in done:
            exception = future.exception()
            if exception:
                break

        self.result = GenerateResult(
            invalid_lines=self._state.invalid_lines,
            exception=exception,
            time_elapsed=end_time - self._state.start_time,
            total=self._state.total,
        )
        if self._result_listener:
            self._result_listener(self.result)

    def _parse_input(self) -> None:
        lines = [line.strip() for line in self._input_text.split("\n")]
        self._state.total = len(lines)
        self._notify_progress()
        for index, line in enumerate(lines):
            if not self._state.running:
                break
            if line.strip() == "":
                self._skip_item()
                continue
            position = index + 1
            try:
                contact = parse_contact(line)
                vcard = serialize_to_vcard(contact)

                self._write_queue.put(WriteQueueItem(row_position=position, origin_content=line, vcard=vcard))
            except PhoneNotFoundError as e:
                self._finish_item()
                _logger.warning(f"Phone not found at line {position}: {e}")
                with self._lock:
                    self._state.invalid_lines.append(InvalidLine(row_position=position, content=line, exception=e))
            except Exception as e:
                self._finish_item()
                _logger.warning(f"Parsing error at line {position}", exc_info=e)
                with self._lock:
                    self._state.invalid_lines.append(InvalidLine(row_position=position, content=line, exception=e))

        self._write_queue.put(None)  # 结束信号

    def _write_output(self):
        while self._state.running and ((item := self._write_queue.get()) is not None):
            try:
                self._output_io.write(item.vcard)
                self._output_io.write("\n\n")
            except Exception as e:
                _logger.warning(f"Unexpected writing error at line {item.row_position}", exc_info=e)
                with self._lock:
                    self._state.invalid_lines.append(
                        InvalidLine(row_position=item.row_position, content=item.origin_content, exception=e)
                    )
            finally:
                # self._write_queue.task_done()
                self._finish_item()

    def _notify_progress(self):
        if self._progress_listener is None:
            return
        self._progress_listener(self._state.progress, self._state.total > 0)

    def _update_progress(self):
        if self._state.total == 0:
            return
        new_progress = round(min(self._state.processed / self._state.total, 1.0), 1)
        if self._state.progress != new_progress:
            with self._progress_lock:
                if self._state.progress != new_progress:
                    self._state.progress = new_progress
                    self._notify_progress()

    def _skip_item(self):
        with self._count_lock:
            self._state.total -= 1
        self._update_progress()

    def _finish_item(self):
        with self._processed_lock:
            self._state.processed += 1
        self._update_progress()
