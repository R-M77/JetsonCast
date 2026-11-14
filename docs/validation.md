# Validation and hardware evidence

The setup layer is an early release, not a certification for every computer,
phone, TV, adapter or network.

- The initial Ubuntu 22.04 ARM64 checks covered archive traversal, special
  permissions, symlinks, hardlinks, ownership markers, ASAR integrity,
  private-data detection and app-only audio routing. Device selection and
  installer tests simulate host metadata to check CPU, OS and profile
  mismatches, the headless dry run and stopping before installation if a
  runtime library is missing. They do not run Electron or simulate a TV.
- The ambient module test verifies actual image reads, the exact 300-second
  boundary, all four backgrounds and wraparound, timed mascot visits, dismissal
  on media load/playback/input, and removal of image sources during playback.
- Background replacement waits for image decoding, retains the current image
  if decoding fails, and discards late results after playback starts. Clock
  text is updated only when its displayed value changes. These checks prevent
  specific redraw/transition problems; physical display flicker needs TV testing.
- A disposable ARM64 installation successfully downloads, verifies, extracts
  and patches the pinned upstream release, creates the launchers, uninstalls
  without deleting unrelated files, preserves the profile, and reinstalls.
- The installed ARM64 Electron runtime starts in an isolated X11 virtual
  display with discovery disabled; no global sandbox-disabling flag is used.
- The x86-64 upstream archive passes digest verification, safe extraction and
  patching. The repacked ASAR is readable by the independent Electron ASAR
  tooling. Physical x86-64 TV playback has **not** been tested.
- The original physical setup was a Jetson Orin Nano 8 GB running Ubuntu 22.04
  ARM64 with X11. YouTube phone casting, fullscreen TV playback and sound were
  user-confirmed, and animated ambient mode was visually verified. No physical
  playback test has been run on an x86-64 mini PC, laptop or desktop, a
  Raspberry Pi 4/5, or another ARM64 board. Ubuntu 24.04 startup and Wayland
  playback remain unverified. See [device guides](../devices/) for each setup.
- Tracked files, staged blobs and initial commit history are scanned for
  common secret/private-data patterns; image metadata is inspected. No real
  user screenshots, browser profiles, device configuration or workspace
  history are included. This is evidence of checks, not a zero-risk guarantee.

Run the repeatable checks:

```sh
python3 -m unittest discover -s tests -v
node tests/test_ambient.cjs
python3 scripts/privacy_check.py --history
python3 install.py devices
python3 install.py --dry-run --non-interactive
```

Node is only needed for the JavaScript test, **not installation**. Hosted CI
runs the tests and privacy guard; hardware behavior requires a real TV.
