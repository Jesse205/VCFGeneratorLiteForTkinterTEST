import math
import platform
import sys


def get_bits() -> int:
    return int(math.log(sys.maxsize + 1, 2) + 1)


def get_machine() -> str:
    return platform.machine().lower()
