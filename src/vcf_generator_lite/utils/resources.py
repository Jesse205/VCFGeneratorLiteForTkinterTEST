import importlib.resources

# 使用 .joinpath("resources") 以兼容 Python3.12
# https://github.com/python/importlib_resources/issues/287
traversable = importlib.resources.files("vcf_generator_lite").joinpath("resources")


def read_text(resource: str, *, encoding: str = "utf-8") -> str:
    # 为了兼容 Python3.12 及以下版本，不能使用 importlib.resources.read_text
    return traversable.joinpath(resource).read_text(encoding=encoding)


def read_binary(resource: str) -> bytes:
    # 为了兼容 Python3.12 及以下版本，不能使用 importlib.resources.read_binary
    return traversable.joinpath(resource).read_bytes()


def read_scaled_binary(
    resources: dict[float, str],
    scaling: float,
) -> bytes:
    if scaling in resources:
        return read_binary(resources[scaling])
    available: list[float] = [scaled for scaled in resources.keys() if scaled <= scaling or scaled == 1.0]
    closest = min(available, key=lambda scaled: scaling - scaled)
    return read_binary(resources[closest])
