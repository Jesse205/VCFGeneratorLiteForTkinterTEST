import importlib.resources
import sys
from collections.abc import Callable

__module = sys.modules[__name__]


def read_text(resource: str, encoding: str = "utf-8", errors: str = "strict") -> str:
    return importlib.resources.read_text(__module, resource, encoding=encoding, errors=errors)


def read_binary(resource: str) -> bytes:
    return importlib.resources.read_binary(__module, resource)


def read_binary_variant[I](
    resource: str,
    variants: list[tuple[I, str]],
    condition: Callable[[I], bool],
) -> bytes:
    for key, resource in variants:
        if condition(key):
            return read_binary(resource)
    else:
        return read_binary(resource)
