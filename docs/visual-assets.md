# Visual sources

| Asset family | Generated reference | Implementation |
| --- | --- | --- |
| README identity, TV/phone composition and feature icons | `assets/design-reference.png` | Editable `assets/hero.svg`: navy field, mint underline, large left-aligned title, rounded mint device outlines, play/phone/shield/ambient icon system. |
| Aurora, coast, meadow and orbital dawn | `assets/references/aurora-lake.png`, `golden-coast.png`, `moonlit-meadow.png`, `orbital-dawn.png` in the same directory | Matching GIFs in `assets/`; the meadow keeps all scenery fixed and animates only isolated firefly glows. The cloudy mountain and waterfall scenes are retired. |
| Jet mascot: open eyes and blink | `assets/references/jet-simple-sheet.png` | `assets/jet-open.png` and `assets/jet-blink.png`; aligned transparent sprites, animated with editable CSS in `src/ambient.js`. |
| Jet walking, crouching and hopping | `assets/references/jet-actions-sheet.png` | `assets/jet-actions.png`: six normalized 256-pixel frames, shared scale and floor anchor; CSS gait and a short hop. Existing idle sprites provide side/top peeks. |
| Ambient overlay | Existing approved ambient layout over the landscape artwork | Editable DOM/CSS in `src/ambient.js`; live time/date and receiver name are text, not baked into images. |
| README previews | The same generated landscape/Jet references and actual ambient module | `assets/previews/screensaver.png` and `assets/previews/jet.gif`; isolated browser rendering with a fictional clock/date, no live desktop or account imagery. |
| Demo phone/TV UI, typography, motion layout and end card | `assets/references/demo-direction.png`, plus the approved landscape and Jet references above | Native graphics composed into `assets/previews/demo-landscape.mp4`, `demo-vertical.mp4`, `demo.gif` and `demo-poster.png`. Illustrated phone UI; no account capture. |
| Compact README identity | `assets/references/jet-simple-sheet.png` | Existing `assets/jet-open.png` displayed at 42 pixels beside a native-text heading. Ad-blocking copy stays editable and the demo appears directly below the introduction. |
| Compact animated banner: layout, TV, Linux PC, HDMI link, phone controls and optional toggle | `assets/references/banner-direction.png`; existing coast, meadow and Jet references above | Editable native composition in `scripts/render_banner.py`; `assets/previews/banner.gif` and `banner-poster.png`. Persistent ad-blocking/old-TV headline, explicit HDMI connection, distinct phone controls, optional Jet peek. Generated direction was inspected before implementation; approved artwork is reused. |
| Demo title-card direction | `assets/hero-adblocking.png`, generated using `assets/references/jet-simple-sheet.png` | Earlier visual reference for the ad-blocking headline and mint/ivory/navy palette. The oversized illustrated banner is retired from the README and sharing kit. |

No real user, device, desktop, account or network screenshots are used. PNG
text/EXIF metadata is removed; GIFs contain only standard animation metadata.
Native Codex image tooling supplied the artwork; its backend model identifier
was not exposed. New landscape artwork is resampled to 1920×1080 and animated
locally into approximately six-second loops at eight frames per second, or
twelve for the meadow. These are animated illustrations, not generated video footage.
Only the current GIF is loaded; it is unloaded during playback.

Jet has a yellow collar tag and a simplified, rounder silhouette. Fun mode is
off by default; when enabled, he visits for
15 seconds after 15–25 seconds of ambient mode, then returns 45–75 seconds
after each visit ends. Visits alternate among short left/right strolls with a
hop down and peeks from the left, right, top or bottom. No action repeats
immediately. Walks last seven seconds within the same visit schedule; peeks
last fifteen. Safe placement keeps Jet away from the clock and instruction.
Playback, media loading or user input immediately hides him and unloads all
mascot images. Reduced-motion preferences disable mascot visits.
