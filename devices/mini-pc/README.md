# Intel or AMD mini PC

**Archive verified:** Jetson Cast verified and patched the x86-64 runtime download. Casting, graphics and HDMI audio have not been physically tested on a mini PC.

1. Use a 64-bit Intel or AMD mini PC running [Ubuntu Desktop](https://documentation.ubuntu.com/desktop/en/latest/) 22.04 or 24.04. Check that Ubuntu already displays on the TV and plays sound through it. Ubuntu 24.04 can [block portable Electron at startup](../../docs/compatibility.md#electron-sandbox-startup).
2. Use the mini PC's HDMI output if present. If it uses DisplayPort or USB-C, check that the chosen port supports display output and that the TV adapter carries audio. Start with a direct connection to the TV to rule out adapter or receiver problems.
3. From the checkout, run `python3 install.py --device mini-pc`. Then [launch and cast](../README.md#set-up-the-computer-connected-to-your-tv). Try one video at 1080p before testing higher resolutions. Verify sound and test wake from sleep before using the mini PC as a dedicated TV receiver.
