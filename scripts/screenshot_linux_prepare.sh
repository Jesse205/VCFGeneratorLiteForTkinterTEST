#!/usr/bin/env bash
# 准备 Linux 对比截图所需主题资产：Xfce42 原 1x 装饰、Breeze/Arc 系 2x 装饰、外部 ttk 主题源码。
# 依赖（apt）：xfwm4 xfwm4-theme-breeze arc-theme imagemagick curl unzip python3。
set -euo pipefail

THEMES="$HOME/.themes"
TTK="$HOME/.local/share/ttk-themes"
mkdir -p "$THEMES" "$TTK"

if [ ! -d "$THEMES/Xfce42-Default/xfwm4" ]; then
    curl -fsSL --retry 3 -o /tmp/xfwm4-4.2.0.tar.gz \
        https://archive.xfce.org/src/xfce/xfwm4/4.2/xfwm4-4.2.0.tar.gz
    tar xzf /tmp/xfwm4-4.2.0.tar.gz -C /tmp xfwm4-4.2.0/themes/default
    mkdir -p "$THEMES/Xfce42-Default/xfwm4"
    cp /tmp/xfwm4-4.2.0/themes/default/*.xpm /tmp/xfwm4-4.2.0/themes/default/*.png \
        /tmp/xfwm4-4.2.0/themes/default/themerc "$THEMES/Xfce42-Default/xfwm4/"
    # 上游源码包中该 xpm 缺行损坏，隔离后 xfwm4 回退同名 png。
    mv "$THEMES/Xfce42-Default/xfwm4/title-1-inactive.xpm" "$THEMES/Xfce42-Default/xfwm4/title-1-inactive.xpm.broken"
fi

for theme in Breeze Arc Arc-Dark Arc-Darker Arc-Lighter; do
    target="$THEMES/$theme-2x/xfwm4"
    if [ ! -d "$target" ]; then
        mkdir -p "$target"
        cp "/usr/share/themes/$theme/xfwm4/"* "$target/"
        python3 "$(dirname "$0")/scale_xpm.py" 2 "$target"
        for f in "$target"/*.png; do
            [ -e "$f" ] || continue
            convert "$f" -filter point -resize 200% "$f.tmp"
            mv "$f.tmp" "$f"
        done
    fi
done

if [ ! -d "$TTK/maxperl" ]; then
    curl -fsSL --retry 3 -o /tmp/ttk-breeze.tar.gz https://codeload.github.com/MaxPerl/ttk-Breeze/tar.gz/refs/heads/master
    mkdir -p "$TTK/maxperl"
    tar xzf /tmp/ttk-breeze.tar.gz -C "$TTK/maxperl" --strip-components=1
fi
if [ ! -d "$TTK/thindil" ]; then
    curl -fsSL --retry 3 -o /tmp/tkbreeze.tar.gz https://codeload.github.com/thindil/tkBreeze/tar.gz/refs/heads/master
    mkdir -p "$TTK/thindil"
    tar xzf /tmp/tkbreeze.tar.gz -C "$TTK/thindil" --strip-components=1
fi
if [ ! -d "$TTK/awthemes" ]; then
    curl -fsSL --retry 3 -o /tmp/awthemes.zip https://sourceforge.net/projects/tcl-awthemes/files/latest/download
    mkdir -p "$TTK/awthemes"
    unzip -q -o /tmp/awthemes.zip -d "$TTK/awthemes"
fi
if [ ! -d "$TTK/sgolovan-arc" ]; then
    curl -fsSL --retry 3 -o /tmp/ttk-themes.zip "https://chiselapp.com/user/sgolovan/repository/ttk-themes/zip/ttk-themes.zip?ci=tip"
    mkdir -p "$TTK/sgolovan-arc"
    unzip -q -o /tmp/ttk-themes.zip -d "$TTK/sgolovan-arc"
fi
echo PREPARE_DONE