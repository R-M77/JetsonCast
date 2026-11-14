# NVIDIA Jetson Orin Nano

**Physical setup tested:** 8 GB Jetson Orin Nano, Ubuntu 22.04 ARM64, X11. The project was developed on this setup. Other Jetson models, Ubuntu 24.04 and Wayland do not share that verification.

1. Sign in to the graphical Ubuntu desktop on your Jetson. For a fresh developer kit, follow [NVIDIA's Jetson Linux setup documentation](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/setup_bsp.html) for the release you intend to use. Jetson Cast does not flash firmware or change JetPack.
2. Use the developer kit's DisplayPort. For an HDMI-only TV, use a DisplayPort-to-HDMI adapter or cable that carries audio. The developer kit's USB-C port cannot drive the display. See [NVIDIA's connector guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html#displayport-output).
3. From the checkout, run `python3 install.py --device jetson-orin-nano`. Select your TV audio output, or follow the desktop default. Then [launch and cast](../README.md#set-up-the-computer-connected-to-your-tv).

If the TV is detected but silent, switch to its input before opening Jetson Cast, then check Ubuntu's Sound panel and test the DisplayPort or HDMI output there. For playback or idle problems on a newer OS, check the [compatibility notes](../../docs/compatibility.md).
