#!/usr/bin/env bash
# Linux 对比截图组合运行器：clam 1x + Xfce42 原装饰；breeze/arc 系 2x。
# 用法：screenshot_linux_combos.sh <输出根目录>；须在已准备资产与 venv 的仓库根运行。
set -u
OUT=${1:?用法: screenshot_linux_combos.sh <输出根目录>}
TTK="$HOME/.local/share/ttk-themes"
PY=${SHOT_PYTHON:-.venv/bin/python}

shot() { # name dpi wm layout font scale ttk themedir
    local name=$1 dpi=$2 wm=$3 layout=$4 font=$5 scale=$6 ttk=$7 dir=$8
    local extra=()
    if [ "$dir" != NONE ]; then
        extra=(--theme-dir "$dir")
    fi
    SHOT_DPI=$dpi SHOT_WM_THEME=$wm SHOT_BUTTON_LAYOUT=$layout SHOT_TITLE_FONT=$font \
        xvfb-run -a -s "-screen 0 1600x1600x24 -dpi $dpi" dbus-run-session -- \
        "$PY" -m scripts.screenshot --platform linux --scale "$scale" --ttk-theme "$ttk" \
        "${extra[@]}" --output-dir "$OUT/$name" >"/tmp/combo-$name.log" 2>&1
    echo "$name exit=$?"
}

# 最终对比组合：clam 1x + 白breeze（maxperl ttk + Breeze-Light 浅色装饰）+ 白arc（arc ttk + 同名 Arc 装饰）。
shot clam-1x-xfce42 96 Xfce42-Default 'O|STHMC' 'Noto Sans 9' 1.0 clam NONE
shot breeze-maxperl-2x 192 Breeze-Light-2x 'O|HMC' 'Noto Sans 18' 2.0 Breeze "$TTK/maxperl"
shot arc-2x 192 Arc-2x 'O|HMC' 'Noto Sans 18' 2.0 arc "$TTK/sgolovan-arc/ttk-themes/themes/Arc"
echo COMBOS_DONE
