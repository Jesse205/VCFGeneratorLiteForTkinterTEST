import binascii
import logging
from concurrent.futures import FIRST_EXCEPTION, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from queue import Queue
from typing import Callable, IO, Optional

from vcf_generator_lite.models.contact import Contact, parse_contact

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InvalidLine:
    row_position: int
    content: str
    exception_str: str


@dataclass
class VCardGeneratorState:
    total: int
    processed: int
    progress: float
    invalid_lines: list[InvalidLine]
    exceptions: list[BaseException]


@dataclass(frozen=True)
class GenerateResult:
    invalid_lines: list[InvalidLine]
    exceptions: list[BaseException]


def utf8_to_qp(text: str) -> str:
    return binascii.b2a_qp(text.encode("utf-8")).decode("utf-8")


def serialize_to_vcard(contact: Contact):
    items: list[str] = [
        "VERSION:2.1",
        f"FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{utf8_to_qp(contact.name)}",
        f"TEL;CELL:{contact.phone}"
    ]
    if contact.note:
        items.append(f"NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{utf8_to_qp(contact.note)}")
    return f"""BEGIN:VCARD
{"\n".join(items)}
END:VCARD"""


class VCFGeneratorTask:
    def __init__(
        self,
        executor: ThreadPoolExecutor,
        progress_listener: Optional[Callable[[float, bool], None]],
        input_text: str,
        output_io: IO
    ):
        self._executor = executor
        self._progress_listener = progress_listener
        self._input_text = input_text
        self._output_io = output_io
        self._state = VCardGeneratorState(
            total=0,
            processed=0,
            progress=0.0,
            invalid_lines=[],
            exceptions=[]
        )
        self._write_queue = Queue()

    def start(self) -> Future[GenerateResult]:
        future = self._executor.submit(self._process)
        return future

    def _process(self) -> GenerateResult:
        with ThreadPoolExecutor(max_workers=2) as pipeline_executor:
            parse_future = pipeline_executor.submit(self._parse_input)
            write_future = pipeline_executor.submit(self._write_output)
            done, _ = wait([parse_future, write_future], return_when=FIRST_EXCEPTION)

            # 收集异常
            for future in done:
                if exception := future.exception():
                    self._state.exceptions.append(exception)
        return GenerateResult(
            invalid_lines=self._state.invalid_lines,
            exceptions=self._state.exceptions
        )

    def _parse_input(self):
        lines = [line.strip() for line in self._input_text.split("\n")]
        self._state.total = len(lines)
        self._notify_progress()
        for position, line in enumerate(lines):
            if line.strip() == "":
                self._on_skip_item()
                continue
            try:
                contact = parse_contact(line)
                vcard = serialize_to_vcard(contact)
                self._write_queue.put(vcard)
            except ValueError as e:
                _logger.warning(f"Invalid contact data at line {position}: {e}")
                self._state.invalid_lines.append(InvalidLine(position, line, str(e)))
                self._on_skip_item()
            except Exception as e:
                _logger.exception(f"Unexpected parsing error at line {position}", exc_info=e)
                self._state.exceptions.append(e)
                self._on_skip_item()
        self._write_queue.put(None)  # 结束信号

    def _write_output(self):
        try:
            while (item := self._write_queue.get()) is not None:
                self._output_io.write(item)
                self._output_io.write("\n\n")
                self._write_queue.task_done()
                self._on_write_item_done()
        except IOError as e:
            _logger.error(f"File write error %s", exc_info=e)
            self._state.exceptions.append(e)
        except Exception as e:
            _logger.exception("Unexpected write error %s", exc_info=e)
            self._state.exceptions.append(e)

    def _notify_progress(self):
        if self._progress_listener is None:
            return
        self._progress_listener(self._state.progress, self._state.total > 0)

    def _increment_progress(self, increment: int = 1):
        if self._state.total == 0:
            return
        self._state.processed += increment
        new_progress = round(min(self._state.processed / self._state.total, 1.0), 1)
        if self._state.progress != new_progress:
            self._state.progress = new_progress
            self._notify_progress()

    def _on_write_item_done(self):
        self._increment_progress()

    def _on_skip_item(self):
        self._increment_progress()
