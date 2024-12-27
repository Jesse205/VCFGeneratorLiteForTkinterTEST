import os
from concurrent.futures import ThreadPoolExecutor, Future
from queue import ShutDown

io_executor = ThreadPoolExecutor(32, "IOThreadPoolExecutor")
cpu_executor = ThreadPoolExecutor(min(32, (os.process_cpu_count() or 1) + 4), "CPUThreadPoolExecutor")


def print_future_result(future: Future):
    if type(future.exception()) is ShutDown:
        return
    print(future.result())
