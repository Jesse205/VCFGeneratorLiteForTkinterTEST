import importlib.resources

# 使用 .joinpath("resources") 以兼容 Python3.12
# https://github.com/python/importlib_resources/issues/287
traversable = importlib.resources.files("vcf_generator_lite").joinpath("resources")


def read_binary(resource: str) -> bytes:
    # 为了兼容 Python3.12 及以下版本，不能使用 importlib.resources.read_binary
    return traversable.joinpath(resource).read_bytes()
