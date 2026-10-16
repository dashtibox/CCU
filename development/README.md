# CB-VIS-CCU-V2.0 bring-up

Recorded: 2026-10-15 (PC date). The board clock is incorrect and reports July 2026.

## Hardware and starting point

The custom carrier uses the previous Mallow Verdin AM62 module and its existing
Torizon installation. The Ethernet connector is not soldered yet. The inherited
Wi-Fi access point is `Verdin-AM62`, with the board at `192.168.50.1`.

Unlike Mallow, this carrier has a TS3USB221ERSER USB 2.0 data switch:

| Connection | Wiring |
| --- | --- |
| Common D+/D- | Verdin USB1 |
| 1D+/1D- | ChargeBridge 2x9 header |
| 2D+/2D- | External USB-C OTG connector |
| S | Verdin GPIO_4, SODIMM 212, pulled down |
| Active-low OE | Ground, switch always enabled |

GPIO_4 low selects ChargeBridge; high selects USB-C. These paths cannot be used
simultaneously. GPIO_4 is MCU_GPIO0_4, not main GPIO0_4. The running kernel labels
its controller `4201000.gpio`, with line offset 4. Its observed sysfs number was
519; the saved script discovers the base rather than assuming that number.

References: [TI switch datasheet](https://www.ti.com/lit/ds/symlink/ts3usb221e.pdf),
[Verdin AM62 pin mapping](https://docs.toradex.com/113758-verdin-am62-datasheet.pdf).

## Working USB connection

Connect the PC to the CCU USB-C OTG connector with a data cable.

- CCU: `192.168.77.1/24`, device MAC `02:00:00:77:00:01`.
- PC: `192.168.77.2/24`, host MAC `02:00:00:77:00:02`.
- Status page: `http://192.168.77.1:8088/`.
- SSH user: `torizon`; use separately maintained credentials.
- USB identity: `0525:a4a2`, Linux USB Ethernet/RNDIS gadget.

The original Mallow service forced both USB controllers into host mode. Its CCU
drop-in now sets only `31100000.usb` to host. `ccu-usb-device.service` selects
GPIO_4 high, sets `31000000.usb` to device mode, loads `g_ether`, and configures
the board's `usb0` address. Its settings are enabled at every boot.

The PC connection must match the host MAC, not a fixed interface name: the first
connection appeared as `usb0`, then as `enx020000770002` after a power cycle.
Keep this connection without a default route so normal Wi-Fi retains internet.

For a PC without an existing `CCU-USB` profile:

```sh
nmcli connection add type ethernet con-name CCU-USB ifname '*' \
  802-3-ethernet.mac-address 02:00:00:77:00:02 \
  ipv4.method manual ipv4.addresses 192.168.77.2/24 \
  ipv4.never-default yes ipv6.never-default yes
nmcli connection up CCU-USB
```

Do not switch the PC's only Wi-Fi adapter to the board AP during normal work:
the AP is local-only and that switch interrupts internet. Initial setup used
short autonomous Wi-Fi sessions with a separate timed internet-restoration job.

## LED

`ccu-led-blink.service` configures `/sys/class/leds/green:debug-1` with the kernel
timer trigger: 500 ms on, 500 ms off. It starts automatically at boot.

The existing web page's LED buttons override this timer. Restore blinking with:

```sh
sudo systemctl restart ccu-led-blink.service
```

Blinking confirms the kernel LED timer is running, not that EVerest or
ChargeBridge is healthy.

## Install on the existing Mallow-derived image

The `board/` tree mirrors absolute board paths. This is an incremental
configuration, not a complete OS image. It requires the existing
`chargebridge-usbc-host.service`, debugfs USB role controls, GPIO sysfs support,
`g_ether`, and the current LED device.

Back up matching destination files first. Copy the contents of `board/` to `/`
on the board using administrator privileges, then run:

```sh
sudo chmod 755 /usr/local/sbin/ccu-usb-device /usr/local/sbin/ccu-led-blink
sudo systemd-analyze verify /etc/systemd/system/ccu-usb-device.service \
  /etc/systemd/system/ccu-led-blink.service
sudo systemctl daemon-reload
sudo systemctl enable --now ccu-usb-device.service ccu-led-blink.service
```

Changing the USB role can interrupt an existing USB connection. The original
host-service unit was backed up on the board under
`/var/home/torizon/ccu-backup-<timestamp>/`.

## Verification completed

1. Selected GPIO_4 high; USB gadget changed from `not attached` to `configured`.
2. PC enumerated `0525:a4a2` and successfully pinged `192.168.77.1`.
3. Loaded the existing status page through USB.
4. Verified both new systemd services active and enabled, with timer 500/500 ms.
5. Issued `systemctl poweroff` over USB; USB disconnected.
6. User removed and restored power.
7. USB enumerated again, both services started successfully, and timer settings
   remained 500/500 ms. Updated the PC profile to match the stable MAC address.
8. SSH over USB verified the post-power-cycle state while PC Wi-Fi stayed online.

Useful checks:

```sh
systemctl is-enabled ccu-usb-device.service ccu-led-blink.service
systemctl is-active ccu-usb-device.service ccu-led-blink.service
cat /sys/class/udc/31000000.usb/state
ip -br addr show usb0
cat /sys/class/leds/green:debug-1/trigger
cat /sys/class/leds/green:debug-1/delay_on /sys/class/leds/green:debug-1/delay_off
```

## Remaining work

- ChargeBridge operation through the new header has not been tested. Current
  startup selects PC USB-C access, disconnecting the ChargeBridge header path.
- A future ChargeBridge mode must select GPIO_4 low and restore USB1 host mode.
- Correct the board clock and investigate its time-sync/provisioning boot wait.
- Solder and validate Ethernet; validate other carrier peripherals separately.
- Never commit passwords, private keys, tokens, or private recovery notebooks.
