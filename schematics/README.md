# Hardware schematics

Original PDFs supplied by the board designer, copied unchanged from Downloads.
The CCU and ACDC drawings were archived on 2026-10-17; the level-shifter drawing
was added on 2026-11-10 with software/documentation revision `display-v1.0.0`.

| Document | PDF pages | Description |
| --- | --- | --- |
| [CB-VIS-ACDC-V1.0](cb-vis-acdc-v1.0%20Schematics.PDF) | 13 | Power, Ethernet, ChargeBridge, ADCs, output interfaces, headers, and mechanical sheets |
| [CB-VIS-CCU-V2.0](cb-vis-ccu-v2.0%20schematics.pdf) | 18 | Verdin carrier power, USB, Ethernet, display/camera interfaces, PCIe, SD, headers, TPM, and mechanical sheets |
| [CB-VIS-LEVELSHIFT-V1.0](cb-vis-levelshift-v1.0.pdf) | 5 | X24 LCD/touch adapter, TXS0108E signal translation, TLV75518 1.8 V regulator, and PCB layout |

## Level-shifter / display reference

- PDF page 3, `Level Shifter.SchDoc`: X24 is the CCU side and X24x is the
  display side. IC1 TXS0108EPWR translates GPIO1/2/3 and SPI CS/CLK/MOSI
  between 1.8 V and 3.3 V. OE connects to the 1.8 V rail.
- IC2 TLV75518PDYDR creates 1.8 V from the 3.3 V supply.
- I2C SCL/SDA pass through; the CCU schematic shows their translator at IC13.
- LCD reset and touch reset share GPIO1. PDF page 5 shows the adapter layout.
- The file/revision-history identifies the adapter as V1.0; some drawing title
  blocks retain the older `cb-vis-ccu` / V2.0 template text. The PDF is preserved
  unchanged.

The assembled display showed Hello World on 2026-11-10. See
[display validation and boot setup](../development/display/README.md).

## CCU reference pages

- PDF page 6, `USB_HUB.SchDoc`: IC24 USB5744T-I/2G connects upstream to
  Verdin USB2. Downstream port 4's USB 2.0 D+/D- pass through L22 to
  `USBH4_D_P` / `USBH4_D_N` in the ChargeBridge bus. This custom carrier
  routes port 4; do not assume the stock Mallow unused-port arrangement.
- PDF page 7, `USB_Connectors.SchDoc`: IC17 TS3USB221ERSER switches USB1
  between the ChargeBridge pair (1D) and USB-C (2D). GPIO_4 drives S and
  active-low OE is grounded.
- PDF page 16, `Extension_Header.SchDoc`: X20 carries both USB paths.
  Pins 13/14 are `USB_CHRGB_P/N`; pins 15/16 are `USBH4_D_N/P`.
  GPIO_4 is Verdin SODIMM 212. LED3 is USER_LED_1 (red/green SODIMM 52/54),
  and LED4 is USER_LED_2 (red/green SODIMM 56/58).

These drawings support the intended arrangement of USB1 device-mode PC access
and USB2 hub-port-4 ChargeBridge access concurrently. Actual hub enumeration,
port enablement, assembled wiring, and ChargeBridge operation remain to be
tested; schematic routing alone does not establish runtime operation.

## ACDC reference pages

- PDF page 3: power supply.
- PDF page 5: Ethernet interface.
- PDF page 6: extension header.
- PDF page 8: ChargeBridge interface, including emergency shutdown, user GPIO,
  CP/PP, serial interfaces, and relay signals.
- PDF page 9: ADCs.
- PDF pages 10–12: output interfaces.

Page numbers above are PDF page positions. Text was extracted across both
documents and the CCU USB/header and ACDC ChargeBridge pages were visually
inspected. This is a navigation/reference summary, not a full design review.

## Original-file SHA-256

See `SHA256SUMS` for checksums of the unchanged PDFs.
