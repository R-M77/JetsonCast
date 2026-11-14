# Other ARM64 computers

**Experimental:** The ARM64 runtime is verified on one Jetson setup. A similar processor does not establish GPU, display, audio or video decoding compatibility on other hardware.

1. Confirm your vendor supplies an Ubuntu 22.04 or 24.04 ARM64 image with a working graphical desktop. Use your vendor's installation instructions; Jetson Cast does not provide OS images or board drivers. For Ubuntu 24.04, review the [Electron startup caveat](../../docs/compatibility.md#electron-sandbox-startup).
2. Connect the TV through an output your board supports. Confirm that Ubuntu already displays on the TV and plays audio through it. A 64-bit CPU with a 32-bit operating system cannot use the supplied runtime.
3. From the checkout, run `python3 install.py --device generic-arm64`. Then [launch and cast](../README.md#set-up-the-computer-connected-to-your-tv). Start with a short 720p video and check TV sound before increasing quality. Test discovery, idle mode and a second cast before relying on it.
