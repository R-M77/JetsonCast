# Repurposed Intel or AMD laptop or desktop

**Archive verified:** Jetson Cast verified and patched the x86-64 runtime download. Playback on any particular laptop, desktop, graphics card or dock is untested.

1. Use a 64-bit Intel or AMD computer running [Ubuntu Desktop](https://documentation.ubuntu.com/desktop/en/latest/) 22.04 or 24.04. Verify the TV output and audio in Ubuntu first. For a laptop, leave the lid open during setup so closing it does not suspend the computer. Ubuntu 24.04 has [an unverified Electron startup path](../../docs/compatibility.md#electron-sandbox-startup).
2. Connect HDMI or DisplayPort and select the TV as the primary display in Ubuntu if the app opens on another screen. If the adapter carries video only, use a separate audio output and select it in Ubuntu.
3. From the checkout, run `python3 install.py`, or select this guide with `python3 install.py --device x86-pc`. Then [launch and cast](../README.md#set-up-the-computer-connected-to-your-tv). Start with a 1080p test and lower the quality if older hardware stutters.
