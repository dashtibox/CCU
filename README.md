# CB-VIS-CCU-V2.0

Development records and configuration for the custom Verdin AM62 carrier board.

Latest development revision: **display-v1.0.0** (2026-11-10).

The Phoenix Contact 1335865 LCD now displays **Hello World** through X24 and the
CB-VIS-LEVELSHIFT-V1.0 adapter. A systemd service initializes the display at boot.
The picture was visually confirmed and the installed boot service ran successfully;
a full power cycle with this display service has not yet been verified.

- [Display setup, wiring, installation and checks](development/display/README.md)
- [Revision history](CHANGELOG.md)
- [Development records](development/README.md)
- [Hardware schematics](schematics/README.md)

Hardware remains CB-VIS-CCU-V2.0; the display revision identifies this software
and documentation update, not a new CCU PCB revision.
