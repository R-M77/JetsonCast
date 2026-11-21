# Demo kit

| File | Format | Use |
| --- | --- | --- |
| [Landscape demo](https://r-m77.github.io/R-M77/?play=jetson) | 1920×1080, 27 s, H.264 | README, X, landscape posts |
| [Vertical demo](https://r-m77.github.io/R-M77/?play=vertical) | 1080×1920, 27 s, H.264 | Reels, Shorts, vertical posts |
| [Compact banner](../assets/previews/banner.gif) | 840×360 GIF, 4.8 s, about 308 KiB | README; plays once, then holds; displayed at 560 px wide |
| [Banner still](../assets/previews/banner-poster.png) | 840×360 PNG | Static alternative |
| [Full animated preview](../assets/previews/demo.gif) | 960×540 GIF | Longer demo preview |
| [Poster](../assets/previews/demo-poster.png) | 1920×1080 PNG | Link thumbnail |
| [Jet loop](../assets/previews/jet.gif) | Animated GIF | Mascot close-up |

Both videos are captioned and silent. The phone flow is an illustration, not a
recording of the YouTube app. Scenery is generated artwork; Jet uses the actual
ambient animation. Demo visits and scene changes are accelerated. No personal
account, desktop, device, or network footage is included.

The compact banner uses the approved coast and meadow artwork, illustrated
phone controls, and Jet's existing sprites. Its clock and overlay are composed
for the demo, not recorded from a live TV. Fun mode is optional and off by
default. The full videos remain available above.

To regenerate the compact banner, install Pillow in your development environment
and run `python scripts/render_banner.py --output build/banner`. The approved
render uses Segoe UI (`segoeui.ttf` and `seguisb.ttf`); use `--font-dir` to point
to your own licensed font directory. Fonts are not bundled. Review output before
copying it into `assets/previews/`.

## A post you can adapt

> Block YouTube ads. Revive your old TV.
> Got a spare laptop or mini PC? Run Ubuntu, connect it to your TV, and let
> JetsonCast add YouTube ad blocking, phone casting, and animated screensavers.
> Your TV doesn't need smart apps. Your phone stays the remote.
> Built and tested on Jetson Orin Nano 8GB. No Jetson required.

Credit JetsonCast and VacuumTube. Describe other hardware according to the
[device matrix](../devices/README.md); ad-blocking behavior can change with
YouTube. These files are a sharing kit, not evidence of a public launch. Keep
the repository and media private until the maintainer approves publication.
