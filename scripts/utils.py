import math
import sys


def get_bits() -> int:
    return int(math.log(sys.maxsize + 1, 2) + 1)
