import importlib.resources

base_traversable = importlib.resources.files("vcf_generator_lite.resources")


def read_text(resource: str, *, encoding: str = "utf-8") -> str:
    # 为了兼容Python3.12及以下版本，不能使用 importlib.resources.read_text
    return base_traversable.joinpath(resource).read_text(encoding=encoding)


def read_binary(resource: str) -> bytes:
    # 为了兼容Python3.12及以下版本，不能使用 importlib.resources.read_binary
    return base_traversable.joinpath(resource).read_bytes()


def read_scaled_binary(
    resources: dict[float, str],
    scaling: float,
) -> bytes:
    if scaling in resources:
        return read_binary(resources.get(scaling))
    avaliable = [scaled for scaled in resources.keys() if scaled <= scaling or scaled == 1.0]
    closest = min(avaliable, key=lambda scaled: scaling - scaled)
    return read_binary(resources.get(closest))
