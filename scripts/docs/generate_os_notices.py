import importlib.metadata
import runpy
import sys
import tomllib
from pathlib import Path
from typing import TypedDict

PATH_OS_NOTICE_DATA = Path("os-notices.toml")

Notice = TypedDict(
    "Notice",
    {
        "name": str,
        "dependency": str,
        "repository": str,
        "license": str,
        "license-url": str,
        "copyrights": list[str],
    },
)


class NoticesConfig(TypedDict):
    template: str
    output: str
    notices: list[Notice]


def format_url(url: str, notice: Notice) -> str:
    if "dependency" not in notice:
        return url
    return url.format(version=importlib.metadata.version(notice["dependency"]))


def generate_notices(config: NoticesConfig):
    return [{**notice, "license-url": format_url(notice["license-url"], notice=notice)} for notice in config["notices"]]


def main() -> int:
    with PATH_OS_NOTICE_DATA.open("rb") as f:
        config = NoticesConfig(**tomllib.load(f))

    with Path(config["output"]).open("w", encoding="utf-8") as f:
        make = runpy.run_path(
            config["template"],
        )["make"]
        output = make(generate_notices(config))
        f.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
