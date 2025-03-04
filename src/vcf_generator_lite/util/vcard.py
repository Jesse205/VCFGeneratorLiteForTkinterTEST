import binascii
import logging
from concurrent.futures import Future, ThreadPoolExecutor, FIRST_EXCEPTION, wait
from dataclasses import dataclass
from queue import Queue
from typing import IO, Callable

from vcf_generator_lite.util.contact import parse_contact, Contact

logger = logging.getLogger(__name__)


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


def serialize_to_vcard(contact: Contact):
    name_encoded = binascii.b2a_qp(contact.name.encode("utf-8")).decode("utf-8")
    return f"""BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{name_encoded}
TEL;CELL:{contact.phone}
END:VCARD"""


class VCardFileGenerator:

    def __init__(self, executor: ThreadPoolExecutor):
        self.executor = executor
        self._progress_callbacks = []

    def add_progress_callback(self, callback: Callable[[float, bool], None]):
        """注册进度回调"""
        self._progress_callbacks.append(callback)

    def _notify_progress(self, progress: float, determinate: bool):
        """通知所有进度回调"""
        for callback in self._progress_callbacks:
            callback(progress, determinate)

    def start(self, input_text: str, output_io: IO) -> Future[GenerateResult]:
        """启动生成任务"""

        future = self.executor.submit(
            self._process,
            input_text,
            output_io
        )
        return future

    def _process(
        self,
        input_text: str,
        output_io: IO
    ) -> GenerateResult:
        write_queue = Queue()
        state = VCardGeneratorState(
            total=0,
            processed=0,
            progress=0.0,
            invalid_lines=[],
            exceptions=[]
        )

        with ThreadPoolExecutor(max_workers=2) as pipeline_executor:
            parse_future = pipeline_executor.submit(
                self._parse_input,
                input_text,
                write_queue,
                state
            )

            write_future = pipeline_executor.submit(
                self._write_output,
                write_queue,
                output_io,
                state
            )

            done, _ = wait([parse_future, write_future], return_when=FIRST_EXCEPTION)

            # 收集异常
            for future in done:
                if exception := future.exception():
                    state.exceptions.append(exception)
        return GenerateResult(invalid_lines=state.invalid_lines, exceptions=state.exceptions)

    def _parse_input(
        self,
        input_text: str,
        write_queue: Queue,
        state: VCardGeneratorState
    ):

        lines = [line.strip() for line in input_text.split("\n")]
        state.total = len(lines)

        for position, line in enumerate(lines):
            try:
                if line.strip() != "":
                    contact = parse_contact(line)
                    vcard = serialize_to_vcard(contact)
                    write_queue.put(vcard)
                else:
                    self._update_progress(state, 1)
            except ValueError as e:
                logger.error(f"Invalid contact data at line {position}: {e}")
                state.invalid_lines.append(InvalidLine(position, line, str(e)))
                self._update_progress(state, 1)
            except Exception as e:
                logger.exception(f"Unexpected parsing error at line {position}", exc_info=e)
                state.exceptions.append(e)
                self._update_progress(state, 1)
        write_queue.put(None)  # 结束信号

    def _write_output(
        self,
        queue: Queue,
        output_io: IO,
        state: VCardGeneratorState
    ):
        try:
            while (item := queue.get()) is not None:
                output_io.write(item)
                output_io.write("\n\n")
                queue.task_done()
                self._update_progress(state, 1)
        except IOError as e:
            logger.error(f"File write error %s", e)
            state.exceptions.append(e)
        except Exception as e:
            logger.exception("Unexpected write error %s", e)
            state.exceptions.append(e)

    def _update_progress(self, state: VCardGeneratorState, increment: int):
        if state.total == 0:
            return
        state.processed += increment
        previous_progress = state.progress
        state.progress = round(min(state.processed / state.total, 1.0), 1)
        if state.progress != previous_progress:
            self._notify_progress(progress=state.progress, determinate=True)
