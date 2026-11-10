#!/bin/sh
# Run on the CCU from any working directory. Existing module definitions are preserved.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
board="$repo/development/board"
[ "$(id -u)" -eq 0 ] || { echo 'Run this installer with sudo on the CCU.' >&2; exit 1; }
[ -c /dev/spidev0.0 ] && [ -c /dev/i2c-2 ] || { echo 'Required SPI/I2C devices missing.' >&2; exit 1; }
[ "$(cat /sys/class/gpio/gpiochip515/label)" = '4201000.gpio' ] || { echo 'GPIO mapping does not match this board.' >&2; exit 1; }
(cd "$repo" && sha256sum -c development/display/SHA256SUMS)
python3 -c 'import ast,sys; [ast.parse(open(p).read()) for p in sys.argv[1:]]' "$board"/usr/local/bin/vis*.py
systemd-analyze verify "$board/etc/systemd/system/vis-display-status.service"
backup="/var/backups/vis-display-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
for path in /usr/local/bin/vis-display-status.py /usr/local/bin/vis_ui.py /usr/local/bin/vis_touch.py /usr/local/bin/vis_modules.py /usr/local/bin/vis_battery.py /usr/local/share/vis-display/status /etc/systemd/system/vis-display-status.service; do
    if [ -e "$path" ]; then cp -a --parents "$path" "$backup/"; fi
done
systemctl stop vis-display-status.service 2>/dev/null || true
systemctl disable --now vis-display-hello.service 2>/dev/null || true
for name in vis-display-status.py vis_ui.py vis_touch.py vis_modules.py vis_battery.py; do
    install -D -m 644 "$board/usr/local/bin/$name" "/usr/local/bin/$name"
done
for name in background.rgb565 splash.rgb565 fonts.json batteries.json; do
    install -D -m 644 "$board/usr/local/share/vis-display/status/$name" "/usr/local/share/vis-display/status/$name"
done
if [ ! -e /usr/local/share/vis-display/status/modules.json ]; then
    install -D -m 644 "$board/usr/local/share/vis-display/status/modules.json" /usr/local/share/vis-display/status/modules.json
fi
install -D -m 644 "$board/etc/systemd/system/vis-display-status.service" /etc/systemd/system/vis-display-status.service
systemctl daemon-reload
systemctl enable --now vis-display-status.service
systemctl is-active vis-display-status.service
printf 'Backup: %s\n' "$backup"
