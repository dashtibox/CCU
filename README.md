# CB-VIS-CCU-V2.0

Software, hardware references and development records for the Virginia Industry
Solutions custom Verdin AM62 carrier board.

**Latest revision: [display-v1.1.0](development/display/README.md), 2026-11-10.**

The Phoenix Contact 1335865 touchscreen now runs **ChargeBridge Monitoring**:

- Actual VIS logo at startup, followed by the live monitoring screen.
- ACDC #1 and #2 cards with connection status and EVerest charging state.
- Large gold battery icons; real battery percentage when the vehicle reports it.
- Tap a module for Status, Specs and Options; swipe to scroll and tap Back to return.
- Expandable home list for future modules, with automatic scrolling beyond two.
- Enabled boot service, automatic recovery and faster 4 MHz SPI screen transfers.

The service and files are installed on the CCU and verified running. The user
confirmed colors, touchscreen navigation and the faster display. A complete cold
power-cycle test of this final revision remains pending.

## Documentation

- **[Complete display README](development/display/README.md)** — hardware, boot behavior,
  installation, module configuration, telemetry rules, tests, troubleshooting and recovery.
- [Revision history](CHANGELOG.md)
- [Development records](development/README.md)
- [Hardware schematics](schematics/README.md)
- [Original Hello World bring-up](development/display/hello-world-v1.0.0.md) — historical only.

Hardware remains **CB-VIS-CCU-V2.0**. The display revision identifies software,
assets and documentation, not a new PCB revision. Older USB-role and reset files
in this repository are historical; use the display-specific installer for this update.
