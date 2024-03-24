import math
import platform
import sys


def get_bits():
    return int(math.log(sys.maxsize + 1, 2) + 1)


def get_machine():
    return platform.machine().lower()
