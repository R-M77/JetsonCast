# GMKtec NucBox G5

**Candidate, not physically tested.** This Intel N97 mini PC follows the existing
x86-64 setup. The upstream archive was validated; this model's graphics, Wi-Fi,
audio and video playback were not.

The manufacturer lists a roughly 72 × 72 × 45 mm enclosure, 12GB memory and
dual HDMI outputs. Verify the exact seller configuration, included storage,
power supply and availability before buying. It is a size example, not a claim
that it is the cheapest available computer. [Manufacturer specifications](https://gmktec.com.my/product/intel-alder-lake-n97-mini-pc-nucbox-g5/).

Use the **amd64 (x86-64)** Ubuntu Desktop 22.04 or 24.04 image.
Confirm TV picture/sound and Wi-Fi, then run
`python3 install.py --device mini-pc`. Follow the [mini-PC guide](../mini-pc/),
including the Ubuntu 24.04 sandbox caveat. Other N97/N100/N150 models need their
own driver and playback checks; the CPU family alone is not a certification.
