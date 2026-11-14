# ESP32 and Pico: not JetsonCast hosts

**The current JetsonCast application cannot run on ESP32, ESP32-S3, ESP32-P4,
or Raspberry Pi Pico/Pico 2.** This is an architecture/runtime limitation,
not a missing installer option.

JetsonCast packages VacuumTube's Electron/Chromium desktop player for
**64-bit Linux ARM64 or x86-64**, with a graphical desktop and browser video
playback. [Electron platform support](https://github.com/electron/electron#platform-support).

| Microcontroller | Relevant hardware difference |
| --- | --- |
| ESP32-S3 | 32-bit Xtensa cores and 512KB internal SRAM; external PSRAM does not provide an ARM64/x86-64 Linux desktop runtime. |
| ESP32-P4 | 32-bit RISC-V cores and 768KB HP L2 memory; its display/image peripherals and H.264 encoder do not make it an Electron/YouTube player. |
| Pico 2 | A microcontroller with 520KB SRAM, not a desktop Linux computer. |

Sources: [Espressif S3](https://www.espressif.com/en/products/socs/esp32-s3),
[Espressif P4 datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html),
[Raspberry Pi Pico family](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html).
Assessment checked 2026-11-10; it applies to this application's current architecture.

An ESP32 could be a **future accessory**, such as a physical button, IR bridge
or small status display, with separate firmware and a defined interface to
the Linux host. None of that integration is implemented in this repository.
The Linux computer would still play the video and perform the ad blocking.
