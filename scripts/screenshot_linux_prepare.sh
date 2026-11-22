#!/usr/bin/env bash
# 准备 Linux 对比截图所需主题资产：Xfce42 原 1x 装饰、白arc（Arc）2x 装饰、白breeze 下载装饰、外部 ttk 主题源码。
# 依赖（apt）：xfwm4 arc-theme imagemagick curl unzip python3。
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

# 2x 装饰缩放：最终只对比白breeze（下方下载的 Breeze-Light）与白arc（apt 的 Arc）两个主题。
for theme in Arc; do
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

# Debian 的 xfwm4-theme-breeze 为深色单变体；浅色版取 mjkim0727/xfwm4-breeze（Plasma 5.22）。
if [ ! -d "$THEMES/Breeze-Light-2x/xfwm4" ]; then
    curl -fsSL --retry 3 -o /tmp/xfwm4-breeze-mjkim.tar.gz \
        https://codeload.github.com/mjkim0727/xfwm4-breeze/tar.gz/refs/heads/main
    tar xzf /tmp/xfwm4-breeze-mjkim.tar.gz -C /tmp
    mkdir -p "$THEMES/Breeze-Light-2x"
    # codeload 压缩包顶层目录为 xfwm4-breeze-main（仓库-分支，无 owner 前缀）。
    cp -r /tmp/xfwm4-breeze-*/xfwm-breeze-light/xfwm4 "$THEMES/Breeze-Light-2x/"
    python3 "$(dirname "$0")/scale_xpm.py" 2 "$THEMES/Breeze-Light-2x/xfwm4"
fi

if [ ! -d "$TTK/maxperl" ]; then
    curl -fsSL --retry 3 -o /tmp/ttk-breeze.tar.gz https://codeload.github.com/MaxPerl/ttk-Breeze/tar.gz/refs/heads/master
    mkdir -p "$TTK/maxperl"
    tar xzf /tmp/ttk-breeze.tar.gz -C "$TTK/maxperl" --strip-components=1
fi
if [ ! -d "$TTK/sgolovan-arc" ]; then
    curl -fsSL --retry 3 -o /tmp/ttk-themes.zip "https://chiselapp.com/user/sgolovan/repository/ttk-themes/zip/ttk-themes.zip?ci=tip"
    mkdir -p "$TTK/sgolovan-arc"
    unzip -q -o /tmp/ttk-themes.zip -d "$TTK/sgolovan-arc"
fi
echo PREPARE_DONE
