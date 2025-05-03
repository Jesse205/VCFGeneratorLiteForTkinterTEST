import importlib.metadata
import runpy
import tomllib
from typing import TypedDict

PATH_OS_NOTICE_DATA = "os_notices.toml"

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

NoticesConfig = TypedDict(
    "NoticesConfig", {"template": str, "output": str, "notices": list[Notice]}
)


def format_url(url: str, notice: Notice) -> str:
    if "dependency" not in notice:
        return url
    return url.format(version=importlib.metadata.version(notice["dependency"]))


def generate_notices(config: NoticesConfig):
    return [
        {**notice, "license-url": format_url(notice["license-url"], notice=notice)}
        for notice in config["notices"]
    ]


def main() -> int:
    with open(PATH_OS_NOTICE_DATA, "rb") as f:
        config = NoticesConfig(**tomllib.load(f))

    with open(config["output"], "w", encoding="utf-8") as f:
        output = runpy.run_path(
            config["template"],
            init_globals={"notices": generate_notices(config)},
        )["output"]
        f.write(output)
    return 0
