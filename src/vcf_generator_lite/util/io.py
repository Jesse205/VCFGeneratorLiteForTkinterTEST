from queue import Queue, ShutDown
from typing import IO, AnyStr, Callable


def write_io_from_queue(output_io: IO, queue: Queue[AnyStr], on_write: Callable[[], None] = None):
    try:
        while True:
            content = queue.get()
            output_io.write(content)
            queue.task_done()
            if on_write is not None:
                on_write()
    except ShutDown:
        pass
