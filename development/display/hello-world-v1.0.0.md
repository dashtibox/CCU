# X24 display — display-v1.0.0

Verified 2026-11-10 on `verdin-am62-08893633`, a Verdin AM62 on CB-VIS-CCU-V2.0.
The Phoenix Contact 1335865 LCD displays white **Hello World** text on black.
`vis-display-hello.service` sends the image during Linux startup after SPI and
GPIO sysfs are available. This is a static boot test, not a framebuffer driver,
desktop, charging-status application, or bootloader splash.

## Hardware

- Display: 320 × 240 Phoenix Contact 1335865, ST7789V2 LCD and GT911 touch.
- Adapter: [CB-VIS-LEVELSHIFT-V1.0](../../schematics/cb-vis-levelshift-v1.0.pdf),
  schematic on PDF page 3; CCU attaches to X24 and display to X24x.
- IC1 TXS0108EPWR translates SPI and GPIO between 1.8 V on A and 3.3 V on B.
  IC2 TLV75518PDYDR generates the adapter's 1.8 V supply; OE is tied to 1.8 V.
- Touch I2C passes through the adapter. The CCU's IC13 provides its existing
  1.8 V / 3.3 V translation.

| Signal | X24 pin | Verdin / Linux connection |
| --- | --- | --- |
| LCD chip select | 3 | SPI_1_CS, `/dev/spidev0.0` |
| LCD reset | 4 | GPIO_1, SODIMM 206, `4201000.gpio` offset 1, sysfs 516 |
| LCD command/data | 5 | GPIO_2, SODIMM 208, `4201000.gpio` offset 2, sysfs 517 |
| SPI clock | 6 | SPI_1_CLK |
| SPI MOSI | 7 | SPI_1_MOSI |
| Touch interrupt | 12 | GPIO_3, SODIMM 210, translated by IC1 |
| Touch reset | 13 | Shared with GPIO_1 / LCD reset |
| Touch SCL / SDA | 14 / 15 | I2C_2_DSI, Linux I2C bus 2 |

The display program resets both LCD and touch through GPIO_1. It does not
drive the USB switch GPIO_4 (sysfs 519). Supply and backlight connections are
unchanged; software does not regulate the backlight current.

## Saved runtime files

Paths below are relative to `development/board/` and mirror board paths:

| File | Purpose |
| --- | --- |
| `usr/local/bin/vis-lcd-hello.py` | Standard-library Python initialization and SPI transfer |
| `usr/local/share/vis-display/hello-world.rgb565` | 153,600-byte, big-endian RGB565 frame, 320 × 240 |
| `etc/systemd/system/vis-display-hello.service` | Enabled oneshot boot service, retained active state |

The script uses SPI mode 0, 8-bit words, 500,000 Hz, RGB565 pixel format `0x55`,
and landscape memory-access control `0x60`. Transfers are at most 4,096 bytes.
It asserts the GPIO controller label before using sysfs GPIOs 516 and 517.
These numbers and paths match the tested kernel; review them after an OS or
device-tree change. GPIO1/2 and spidev must not be owned by another display driver.

The unit waits up to 30 seconds for `/dev/spidev0.0` and `gpiochip515`, then runs
the script with a total startup timeout of 45 seconds. The image remains in LCD
memory after the process exits. It is redrawn at the next Linux boot.

## Install only this display update

Run on the CCU from a copy of this repository. Requires Python 3, systemd,
GPIO sysfs, the existing SPI device/pinmux, and the connected level-shifter board.

```sh
backup="/home/torizon/vis-display-backup-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p "$backup"
for file in /usr/local/bin/vis-lcd-hello.py \
  /usr/local/share/vis-display/hello-world.rgb565 \
  /etc/systemd/system/vis-display-hello.service; do
  if test -f "$file"; then sudo cp --parents "$file" "$backup/"; fi
done
sudo install -D -m 755 development/board/usr/local/bin/vis-lcd-hello.py \
  /usr/local/bin/vis-lcd-hello.py
sudo install -D -m 644 development/board/usr/local/share/vis-display/hello-world.rgb565 \
  /usr/local/share/vis-display/hello-world.rgb565
sudo install -D -m 644 development/board/etc/systemd/system/vis-display-hello.service \
  /etc/systemd/system/vis-display-hello.service
sudo systemd-analyze verify /etc/systemd/system/vis-display-hello.service
sudo systemctl daemon-reload
sudo systemctl enable vis-display-hello.service
sudo systemctl restart vis-display-hello.service
```

Install only these three files for this update. The repository also contains
historical USB-role settings whose installation can change the management link.

## Checks and observed results

```sh
systemctl is-enabled vis-display-hello.service
systemctl show vis-display-hello.service -p ActiveState -p SubState -p ExecMainStatus
journalctl -u vis-display-hello.service -n 10 --no-pager
```

Observed: `enabled`, `ActiveState=active`, `SubState=exited`, and
`ExecMainStatus=0`. The user visually confirmed Hello World before persistence
was installed; the same image was then sent successfully by the installed unit.
SPI completion alone cannot prove that pixels are visible.

GT911 identification was read before LCD initialization:

```sh
sudo i2ctransfer -y 2 w2@0x14 0x81 0x40 r4
# Observed: 0x39 0x31 0x31 0x00  (ASCII "911")
```

Address `0x5d` did not respond during that check. The touch address is selected
during reset, so recheck it if reset/interrupt sequencing changes. No touch driver
was configured and touch events have not been tested.

**Pending:** a complete power-off/power-on test confirming the image returns.
No reboot was performed to install or verify this unit. Earlier USB power-cycle
tests do not count as validation of this display revision.

## Disable / rollback

```sh
sudo systemctl disable --now vis-display-hello.service
```

Stopping the oneshot service does not blank the LCD. Restore any previous files
from the backup directory and run `sudo systemctl daemon-reload` if reverting
an earlier installation. The existing screen image lasts until a reset or loss
of display power.
