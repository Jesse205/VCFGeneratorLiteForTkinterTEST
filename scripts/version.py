import packaging.version

from vcf_generator_lite.__version__ import __version__ as app_version

__all__ = ["app_version", "app_windows_ffi_version", "app_windows_version", "get_windows_file_info_version"]


def get_windows_file_info_version(version: str) -> tuple[int, int, int, int]:
    parsed = packaging.version.parse(version)
    build = 0
    match parsed.pre:
        case ("a", _):
            build += 10000
        case ("b", _):
            build += 20000
        case ("rc", _):
            build += 30000
        case _:
            if not parsed.is_devrelease:
                build += 40000
    if parsed.pre:
        build += parsed.pre[1] * 100
    if parsed.post is not None:
        build += parsed.post * 10
    if parsed.dev is not None:
        build += parsed.dev
    return (
        parsed.major,
        parsed.minor,
        parsed.micro,
        build,
    )


app_windows_ffi_version = get_windows_file_info_version(app_version)
app_windows_version = ".".join(str(part) for part in app_windows_ffi_version)
