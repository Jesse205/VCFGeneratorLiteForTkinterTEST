import binascii
import logging
from concurrent.futures import Future, ThreadPoolExecutor, FIRST_EXCEPTION, wait
from dataclasses import dataclass
from queue import Queue
from typing import IO, Callable

from vcf_generator_lite.util.person import parse_person

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LineItem:
    line: int
    content: str


@dataclass(frozen=True)
class GenerateResult:
    invalid_items: list[LineItem]
    exceptions: list[BaseException]


@dataclass
class VCardProcessorState:
    total: int
    processed: int
    progress: float
    invalid_items: list[LineItem]
    exceptions: list[BaseException]


def generate_vcard_entry(name: str, phone: int):
    name_encoded = binascii.b2a_qp(name.encode("utf-8")).decode("utf-8")
    return f"""BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{name_encoded}
TEL;CELL:{phone}
END:VCARD"""


class VCardProcessor:

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

    def generate(self, input_text: str, output_io: IO) -> Future[GenerateResult]:
        """启动生成任务"""
        write_queue = Queue()
        future = self.executor.submit(
            self._process_content,
            input_text,
            write_queue,
            output_io
        )
        return future

    def _process_content(
        self,
        input_text: str,
        write_queue: Queue,
        output_io: IO
    ) -> GenerateResult:
        state = VCardProcessorState(
            total=0,
            processed=0,
            progress=0.0,
            invalid_items=[],
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

        return GenerateResult(invalid_items=state.invalid_items, exceptions=state.exceptions)

    def _parse_input(
        self,
        input_text: str,
        write_queue: Queue,
        state: VCardProcessorState
    ):
        try:
            cleaned_content = input_text.replace("\t", " ").strip()
            items = [
                line.strip() for line in cleaned_content.split("\n")
                if line.strip()
            ]
            state.total = len(items)

            for idx, line in enumerate(items, 1):
                try:
                    person = parse_person(line)
                    vcard = generate_vcard_entry(person.name, person.phone)
                    write_queue.put(vcard)
                except ValueError as e:
                    logger.error(f"Invalid line {idx}: {e}")
                    state.invalid_items.append(LineItem(idx, line))
                    self._update_progress(state, 1)
                except Exception as e:
                    logger.exception(f"Unexpected parsing error")
                    state.exceptions.append(e)
                    self._update_progress(state, 1)
        finally:
            write_queue.put(None)  # 结束信号

    def _write_output(
        self,
        queue: Queue,
        output_io: IO,
        state: VCardProcessorState
    ):
        try:
            while (item := queue.get()) is not None:
                output_io.write(item)
                self._update_progress(state, 1)
        except IOError as e:
            logging.error(f"File write error %s", e)
            state.exceptions.append(e)
        except Exception as e:
            logging.exception("Unexpected write error %s", e)
            state.exceptions.append(e)

    def _update_progress(self, state: VCardProcessorState, increment: int):
        if state.total == 0:
            return
        state.processed += increment
        previous_progress = state.progress
        state.progress = round(min(state.processed / state.total, 1.0), 1)
        if state.progress != previous_progress:
            self._notify_progress(progress=state.progress, determinate=True)
