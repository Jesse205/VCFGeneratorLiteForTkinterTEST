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
        bash scripts/screenshot_linux_env.sh \
        "$PY" -m scripts.screenshot --platform linux --scale "$scale" --ttk-theme "$ttk" \
        "${extra[@]}" --output-dir "$OUT/$name" >"/tmp/combo-$name.log" 2>&1
    echo "$name exit=$?"
}

shot clam-1x-xfce42 96 Xfce42-Default 'O|STHMC' 'Noto Sans 9' 1.0 clam NONE
shot breeze-maxperl-2x 192 Breeze-2x 'O|HMC' 'Noto Sans 18' 2.0 Breeze "$TTK/maxperl"
shot breeze-thindil-2x 192 Breeze-2x 'O|HMC' 'Noto Sans 18' 2.0 breeze "$TTK/thindil"
shot awbreeze-2x 192 Breeze-2x 'O|HMC' 'Noto Sans 18' 2.0 awbreeze "$TTK/awthemes"
shot arc-2x 192 Arc-2x 'O|HMC' 'Noto Sans 18' 2.0 arc "$TTK/sgolovan-arc/ttk-themes/themes/Arc"
shot arc-dark-2x 192 Arc-Dark-2x 'O|HMC' 'Noto Sans 18' 2.0 arc "$TTK/sgolovan-arc/ttk-themes/themes/Arc"
shot arc-darker-2x 192 Arc-Darker-2x 'O|HMC' 'Noto Sans 18' 2.0 arc "$TTK/sgolovan-arc/ttk-themes/themes/Arc"
shot arc-lighter-2x 192 Arc-Lighter-2x 'O|HMC' 'Noto Sans 18' 2.0 arc "$TTK/sgolovan-arc/ttk-themes/themes/Arc"
echo COMBOS_DONE