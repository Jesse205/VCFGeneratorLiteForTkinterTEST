import sys
from queue import Queue
from typing import IO, AnyStr, Callable


def write_io_from_queue(output_io: IO, queue: Queue[AnyStr], on_write: Callable[[int], None] = None):
    write_count = 0
    while True:
        content = queue.get()
        output_io.write(content)
        queue.task_done()
        write_count += 1
        if on_write is not None:
            try:
                on_write(write_count)
            except Exception as e:
                print(e, file=sys.stderr)
