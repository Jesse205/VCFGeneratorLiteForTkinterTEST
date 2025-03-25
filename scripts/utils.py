import math
import sys


def get_bits() -> int:
    return int(math.log(sys.maxsize + 1, 2) + 1)


def require_64_bits() -> None:
    if get_bits() != 64:
        raise RuntimeError(f"64-bit Python is required, but {get_bits()}-bit Python is found.")
