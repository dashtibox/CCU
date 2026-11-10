# Revision history

## display-v1.0.0 — 2026-11-10

- Add the tested ST7789V2 Hello World program, its 320 × 240 RGB565 frame,
  and `vis-display-hello.service` for automatic initialization at boot.
- Archive the exact files installed on the CCU, using persistent paths under
  `/usr/local/bin`, `/usr/local/share/vis-display`, and `/etc/systemd/system`.
- Add the original CB-VIS-LEVELSHIFT-V1.0 schematic and SHA-256 checksum.
- Document X24 wiring, 1.8 V / 3.3 V translation, shared LCD/touch reset,
  SPI mode 0 at 500 kHz, installation, service checks, and rollback.
- Record successful GT911 identification on I2C2 at `0x14` (`39 31 31 00`).
- Update repository descriptions to distinguish current display operation from
  the historical USB/LED snapshot.

Validation: user confirmed visible Hello World; systemd unit verification passed;
service enabled and active (exited), `ExecMainStatus=0`. No full power-cycle test
of the new display service or touchscreen input-event test has been completed.

Hardware identifiers remain CB-VIS-CCU-V2.0 and CB-VIS-LEVELSHIFT-V1.0.

## Earlier records

- 2026-10-17: CCU and ACDC schematic archive and reference index.
- 2026-10-15: USB-C bring-up and persistent LED blink configuration.
