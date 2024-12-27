import os
from concurrent.futures import ThreadPoolExecutor

io_executor = ThreadPoolExecutor(32)
cpu_executor = ThreadPoolExecutor(min(32, (os.process_cpu_count() or 1) + 4))
