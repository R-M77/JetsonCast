# NanoPi and “Pi Nano”

NanoPi is a **FriendlyELEC** board family, not a Raspberry Pi model. The name
alone does not identify a compatible computer. NVIDIA's Jetson Nano is also a
different product from the tested Jetson Orin Nano 8GB.

**No NanoPi model is physically validated for JetsonCast.** A candidate needs
a vendor-supported Ubuntu 22.04/24.04 ARM64 graphical desktop, working graphics
drivers, TV video/audio output, and enough memory for the desktop/player.
Only then follow the [generic ARM64 guide](../generic-arm64/).

Avoid assuming that tiny router boards can drive a TV. For example, the
NanoPi R2S lists 1GB RAM and dual Ethernet but no HDMI/display connector;
it is not a candidate for this TV-connected setup. [FriendlyELEC's R2S hardware documentation](https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R2S).

There is no NanoPi-specific installer profile. A headless Linux boot or working
Docker installation does not validate Electron playback or HDMI audio.
