weston --fullscreen --socket=wayland-10 &
WAYLAND_DISPLAY=wayland-10 Xwayland :1 &
DISPLAY=:1 python -m weigh.gui
