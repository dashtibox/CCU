# ChargeBridge Monitoring — display-v1.1.0

Complete display snapshot from `verdin-am62-08893633`, verified 2026-11-10.
Runtime source and asset checksums match the installed CCU files.

## What appears on screen

During Linux startup, the actual Virginia Industry Solutions logo appears for
four seconds, then **ChargeBridge Monitoring** opens. This is a Linux service
splash, not an image displayed by the bootloader immediately at power application.

The home screen has two cards today: **ACDC #1 / USB** and **ACDC #2 / ETH**.
Connection labels are on the left. Each card shows ChargeBridge connectivity,
the actual EVerest session state and a large gold-and-black battery icon.
The battery artwork is doubled from the initial design: 128×80 rendered pixels,
with empty outer padding trimmed to a 128×70 sprite so both cards fit.

Tap either card to open:

| Tab | Contents |
| --- | --- |
| Status | Bridge connection, charging state, measured current and voltage per phase, power, session energy/duration, separately labeled configured limits |
| Specs | Module/model, connection/IP, EVerest connector, reported capabilities |
| Options | Clearly labeled placeholders for future selections; no controls enabled |

Swipe up/down to scroll detail pages. Back returns to the home list and preserves
its scroll position. With more than two modules, the home screen scrolls and shows
a scrollbar; the logo and footer remain fixed. Additional-module tests used local
fixtures only—no fake modules or messages were added to the installed EVerest system.

## Battery icons and truthful data

| State | Battery appearance |
| --- | --- |
| Unplugged | Resting face and disconnected plug; no percentage |
| Charging, no reported SoC | Lightning bolt; no invented percentage |
| ChargingPausedEV / ChargingPausedEVSE | Pause bars |
| Preparing / authorization required / reserved | Connected/ready plug |
| Finished | Checkmark; does not imply 100% |
| Offline / disabled / faulted | Cross |
| Unknown / waiting | Dots |
| Connected session with fresh `ev_info.soc` | Actual rounded percentage and matching battery fill |

The LCD does not estimate SoC from current, power, connectivity or elapsed time.
Only a finite numeric `ev_info.soc` between 0 and 100 is accepted. Retained, missing,
stale, invalid or disconnected SoC does not produce a percentage. AC charging may
not supply vehicle SoC at all.

The display retains the exact EVerest state (for example `Unplugged`, `Preparing`,
`Charging`); compact paused labels on the home card retain their meaning. It does
not fabricate a generic standby state. Measurements without valid telemetry show
**Unavailable**, not zero.

### State versus measurement freshness

Session state is event-driven and can remain unchanged for hours. It is not
expired simply because no transition occurred for 60 seconds. A state is shown
only with live ChargeBridge connectivity, a recent API heartbeat, and a session
message timestamp at or after the current EVerest service activation time.
Retained messages from earlier EVerest runs are rejected. A decreasing API heartbeat
counter invalidates cached state until a new non-retained session message arrives.

This installation publishes API heartbeats every **40 seconds**; the display
uses a **100-second** timeout. Review that timeout if the EVerest heartbeat interval
changes. The board initially booted with October 25 wall time and later corrected
to November 10. Its current-run `Unplugged` messages therefore looked old, which
caused the previous display's erroneous stale-state label. The revised policy
checks the originating EVerest run rather than transition age alone.

Current, voltage, energy, power and SoC still use measurement freshness checks:
non-retained messages received within 30 seconds, and timestamps within 60 seconds
when provided. Configured limits use 15 seconds; reported capabilities use 120.
Capabilities and current limits are reported configuration, not certified PCB ratings.

## Current module configuration and expansion

Persistent definitions live in:
`/usr/local/share/vis-display/status/modules.json`.

| ID | API connector | Link | IP | Service | Bridge telemetry key |
| --- | --- | --- | --- | --- | --- |
| 1 | `vis_acdc1` | USB | `192.168.5.136` | `pionix-chargebridge` | `cb_eval` |
| 2 | `vis_acdc2` | Ethernet | `192.168.1.247` | `pionix-chargebridge-acdc2` | `cb_acdc2` |

These addresses describe the verified installation and may change with network
configuration. CCU management was available at `192.168.1.238`; no credentials
are stored in this update.

To add a commissioned module, add a unique positive numeric `id` and its actual
`name`, `model`, `chargebridge_model`, `connection`, `ip`, `service`, `bridge_key`
and `connector` to the JSON file, then restart `vis-display-status`. Use actual
values; do not copy module #2's address or service onto another device.

Live, non-retained `session_info` or `hw_capabilities` messages from
`everest_api/1/evse_manager_consumer/vis_acdcN/e2m/` also discover a new entry.
Unknown connection details show **SETUP NEEDED** and specs show **Not configured**.
Discovery does not commission hardware or establish an EVerest connection.
Auto-discovered entries remain for the service lifetime; add them to the JSON
file to keep them listed offline across reboot. The supported topic convention
is `vis_acdcN`; arbitrary connector names need an adapter change.

Configured or discovered modules are sorted by numeric ID. Two fit without
scrolling; more enable scrolling automatically. Tests cover up to 20 entries
and nonconsecutive IDs. The installed configuration contains only IDs 1 and 2.

## Hardware and electrical interface

- CCU: CB-VIS-CCU-V2.0, Verdin AM62.
- Display: Phoenix Contact 1335865, 320×240, ST7789V2 LCD and GT911 touch.
- Adapter: [CB-VIS-LEVELSHIFT-V1.0](../../schematics/cb-vis-levelshift-v1.0.pdf), PDF page 3.
- TXS0108EPWR translates SPI/GPIO between 1.8 V and 3.3 V; TLV75518 supplies 1.8 V.
- Touch I2C passes through the adapter; CCU IC13 supplies the existing translation.

| Signal | X24 pin | Linux connection |
| --- | --- | --- |
| LCD CS | 3 | `/dev/spidev0.0` |
| LCD reset | 4 | GPIO_1, SODIMM 206, sysfs 516 |
| LCD D/C | 5 | GPIO_2, SODIMM 208, sysfs 517 |
| SPI clock / MOSI | 6 / 7 | SPI_1 |
| Touch INT | 12 | GPIO_3, SODIMM 210, sysfs 518 |
| Touch reset | 13 | Shared LCD reset / GPIO_1 |
| Touch SCL / SDA | 14 / 15 | `/dev/i2c-2` |

GPIO controller label must be `4201000.gpio`, base 515. Review numbering after an
OS/device-tree update. GPIO_4 / sysfs 519, the USB selector, is not changed.
The shared reset resets both LCD and touch. Backlight regulation is unchanged.

The GT911 requires INT to participate in reset: reset low 20 ms, select address
with INT high, wait 2 ms, reset high, wait 6 ms, INT low 50 ms, then INT becomes
input. This corrected zero configuration registers to 320×240. The reader probes
0x14 and 0x5d, validates ID `911`, reads coordinates, and acknowledges 0x814e. It
does not flash touch firmware or rewrite its configuration table.

LCD: SPI mode 0, 8 bits, **4 MHz**, RGB565 0x55, landscape MADCTL 0x60,
**INVON 0x21**. INVON is required for the confirmed correct physical colors on
this panel; omitting it produced complementary colors and a white monitoring
background. Data is sent in chunks no larger than 4096 bytes. No desktop,
framebuffer driver or kernel overlay is installed by this update.

## Runtime files and dependencies

Files under `../board/` mirror absolute paths on the CCU:

| Path | Purpose |
| --- | --- |
| `usr/local/bin/vis-display-status.py` | Boot sequence, MQTT, health checks, SPI rendering and watchdog |
| `usr/local/bin/vis_ui.py` | Home/detail layout, touch navigation, scrolling and freshness rules |
| `usr/local/bin/vis_touch.py` | GT911 input via Linux I2C_RDWR |
| `usr/local/bin/vis_modules.py` | Module configuration and discovery |
| `usr/local/bin/vis_battery.py` | Battery status selection and cached sprite drawing |
| `usr/local/share/vis-display/status/` | Background, splash, fonts, modules JSON and battery sprites |
| `etc/systemd/system/vis-display-status.service` | Enabled systemd startup and recovery |

CCU requirements: Python 3 standard library, systemd, GPIO sysfs, SPI/I2C devices,
`ping`, Docker, and existing `everest-mosquitto` container with `mosquitto_sub`.
Pillow is needed only on the PC to rebuild artwork. The monitor subscribes to MQTT;
it never publishes charging commands, toggles relays, or changes EVerest settings.

The service starts independently of network/Docker readiness and retries telemetry.
It waits up to 30 seconds for SPI/GPIO, uses `Type=notify`, a 60-second watchdog,
and restarts after failure. The legacy `vis-display-hello.service` is disabled
and conflicts with this service. Only one process should own LCD SPI/GPIO.

Performance: full-frame transfer measured about 503 ms at 4 MHz, versus a minimum
2.46 seconds of wire time at the earlier 500 kHz. Cached detail text rendering
measured 86 ms versus 146 ms. Pixel comparison confirmed identical rendered colors.
Only changed row groups are sent. Touch and UI polling run at 20 ms; telemetry
redraw checks run every five seconds. This is not a 60-fps UI.

## Install on the CCU

Copy/check out this repository on the board. Run:

```sh
sudo sh development/display/install.sh
```

The installer validates devices/checksums, backs up the previous display files
under `/var/backups/vis-display-<timestamp>/`, disables Hello World, installs the
monitor, enables it and starts it. Existing `modules.json` is preserved on upgrade;
for a first install the two-module reference configuration is installed. It only
installs display files, not historical USB/network/reset configuration.

The installer has been syntax-checked; equivalent individual installation steps
were used on the live CCU. The new installer itself has not been rerun over that
installation. A full cold power-cycle of this final revision remains pending.

## Verify and troubleshoot

```sh
systemctl is-enabled vis-display-status
systemctl show vis-display-status -p ActiveState -p NRestarts -p WatchdogTimestamp
journalctl -u vis-display-status -n 30 --no-pager
cat /run/vis-display-page.json
cat /run/vis-display-perf.json
```

Expected: enabled, active, Touch ready: 320x240, watchdog advancing. The first
session state can wait up to one 40-second API heartbeat interval after startup.
The last transmitted framebuffer is `/run/vis-display-status.rgb565` (153600
bytes, big-endian RGB565); this verifies the intended image, not physical pixels.

- **Wrong colors:** check `cmd(0x21)` is present in initialization.
- **No touch / zero resolution:** check the level shifter and shared reset/INT sequence.
- **NO LINK:** check the configured IP and physical USB/Ethernet connection.
- **SERVICE OFF:** inspect the module's configured Pionix service.
- **SETUP NEEDED:** fill in the new module's connection/bridge metadata.
- **State unavailable:** inspect heartbeat cadence, EVerest activation time and MQTT.
- **Measurements unavailable:** no fresh measurement was received; do not substitute a limit.
- **No battery percentage:** the vehicle may not provide SoC, or that data is stale.
- **Distorted pixels at 4 MHz:** inspect wiring and restore the previous speed if needed.

Source references: [ST7789V2 datasheet](https://files.waveshare.com/upload/c/c9/ST7789V2.pdf),
[GT911 programming guide](https://www.lcd-module.de/fileadmin/eng/pdf/zubehoer/GT911_Programming_Guide_Rev.10.pdf).
The installed EVerest API schema at
`/home/torizon/everest/everest-chargebridge/share/everest/EVerest_API/evse_manager_consumer_API.yaml`
defines `ev_info.soc` and the other consumed payloads.

## Rebuild artwork and run tests

On a development PC with Pillow and DejaVu fonts installed:

```sh
python3 development/display/assets/build-assets.py
python3 development/display/assets/build-batteries.py
```

Generators place output beside themselves. Copy `background.rgb565`,
`splash.rgb565`, `fonts.json` and `batteries.json` into
`development/board/usr/local/share/vis-display/status/`, then regenerate
`SHA256SUMS` before installation. The actual source logo is preserved unchanged.
Runtime Python has no Pillow dependency.

```sh
PYTHONPATH=development/board/usr/local/bin python3 -m unittest discover \
  -s development/display/tests -p 'test_*.py'
sha256sum -c development/display/SHA256SUMS
```

Eighteen tests cover navigation, scroll bounds, discovery, current-vs-limit handling,
stale data, session-state validity, and battery percentage validation. Live service
checks pass; original installed/runtime files have matching SHA-256 values.
User-confirmed: correct colors, functioning touch navigation, improved speed and
visible monitoring screen. No EV charging session, real SoC transfer, additional
physical modules or final cold power-cycle was tested in this display work.

## Disable or restore a previous display

```sh
sudo systemctl disable --now vis-display-status
```

To restore an installer-created backup, substitute its actual timestamp:

```sh
sudo systemctl stop vis-display-status
sudo cp -a /var/backups/vis-display-TIMESTAMP/usr/. /usr/
sudo cp -a /var/backups/vis-display-TIMESTAMP/etc/. /etc/
sudo systemctl daemon-reload
sudo systemctl enable --now vis-display-status
```

These restore commands apply when a previous monitoring installation existed.
Earlier manual-development backups use a flatter layout; inspect them before
restoring. Disabling the service alone leaves the last picture in LCD memory.
The historical Hello World bring-up remains at
[hello-world-v1.0.0.md](hello-world-v1.0.0.md), with its original limitations.
