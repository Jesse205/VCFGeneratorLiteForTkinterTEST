#!/usr/bin/env bash
# Linux 截图环境：Xft DPI、xfwm4 窗口装饰与标题栏字体。
# 须在以 -dpi 192 启动的 Xvfb 与 dbus 会话内运行；配置完成后 exec 传入的命令。
set -euo pipefail

xrdb -merge <<'EOF'
Xft.dpi: 192
EOF

# xfconfd 不在 PATH 中，由 dbus 按服务名自动激活；此处仅等待其就绪。
for _ in $(seq 1 50); do
    if xfconf-query -c xfwm4 -l >/dev/null 2>&1; then
        break
    fi
    sleep 0.1
done

set_property() {
    xfconf-query -c xfwm4 -p "$1" -n -t "$2" -s "$3"
}
set_property /general/theme string Default-xhdpi
set_property /general/title_font string "Noto Sans 9"
set_property /general/title_alignment string left
set_property /general/button_layout string "O|HMC"
set_property /general/use_compositing bool false
set_property /general/show_frame_shadow bool false
set_property /general/show_popup_shadow bool false

xfwm4 &
for _ in $(seq 1 50); do
    if xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | grep -q "window id"; then
        break
    fi
    sleep 0.1
done

exec "$@"