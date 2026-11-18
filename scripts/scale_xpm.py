"""按整数倍点缩放 XPM 像素行，保留符号颜色表（ImageMagick 会破坏符号色）。"""

import re
import sys
from pathlib import Path


def scale_xpm(path: Path, factor: int):
    text = path.read_text(encoding="latin-1")
    strings = re.findall(r'"([^"]*)"', text)
    width, height, ncolors, cpp = (int(v) for v in strings[0].split())
    colors = strings[1 : 1 + ncolors]
    rows = strings[1 + ncolors : 1 + ncolors + height]
    if len(rows) != height:
        print(f"skip malformed {path}: rows {len(rows)} != height {height}")
        return
    new_rows = []
    for row in rows:
        tokens = [row[i : i + cpp] for i in range(0, len(row), cpp)]
        scaled = "".join(token * factor for token in tokens)
        new_rows.extend([scaled] * factor)
    out = ["/* XPM */", "static char *scaled[] = {"]
    out.append(f'"{width * factor} {height * factor} {ncolors} {cpp}",')
    out.extend(f'"{c}",' for c in colors)
    out.extend(f'"{r}",' for r in new_rows[:-1])
    out.extend((f'"{new_rows[-1]}"', "};"))
    path.write_text("\n".join(out) + "\n", encoding="latin-1")


if __name__ == "__main__":
    factor = int(sys.argv[1])
    for path in sorted(Path(sys.argv[2]).glob("*.xpm")):
        scale_xpm(path, factor)
    print(f"scaled {len(list(Path(sys.argv[2]).glob('*.xpm')))} xpm files by {factor}")
