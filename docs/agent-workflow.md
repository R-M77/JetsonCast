# JetsonCast agent workflow

Use only the mode requested. Run commands from the checkout root with the
desktop user's permissions. The skill adds guidance, not authorization to
deploy, publish, change repository visibility, or send messages.

## Set up

1. Read `devices/README.md` and the matching device guide. On the target Linux
   desktop, run `python3 install.py --dry-run --non-interactive` first. Stop
   on an unsupported host; do not bypass the architecture or sandbox checks.
2. Within the user's installation request, run `python3 install.py` in their
   graphical session. Let them select the TV audio output and login autostart.
   Keep credentials out of chat and command arguments.
3. Launch the application, complete its first-run screen, then test phone
   discovery, fullscreen playback, TV sound, and clearing the idle overlay.
   Ask the user for observations when you cannot see or hear the TV. A
   successful install or unit test is not proof of casting or audio.

## Diagnose

Start with `python3 install.py doctor` and `docs/compatibility.md`.
Check desktop availability, active audio output, the phone's local-network
permission, and whether both devices can reach each other. The receiver uses
DIAL for YouTube; it does not emulate every Chromecast application.

Use `python3 install.py configure` for existing settings. Inspect only relevant
files and bounded logs. Do not dump profiles, cookies, tokens, browsing history,
environment variables, or LAN inventories. Summarize diagnostics before sharing.
Keep host DNS, router settings, other agents and containers unchanged. Changing
automatic login, firewall policy, or rebooting is a separate user decision.

## Contribute

Read `CONTRIBUTING.md`, `SECURITY.md`, and `docs/validation.md`. Follow the existing
separation: installer, isolated runtime/profile, launcher/audio, ambient overlay,
and optional input-switch addon. Keep ambient changes isolated from playback;
preserve unload-on-cast, decode-before-swap, and reduced-motion behavior.

Run the relevant checks:

```bash
python3 -m unittest discover -s tests -v
node tests/test_ambient.cjs
python3 scripts/privacy_check.py --history
```

Use synthetic fixtures and reviewed assets. Check all added files as well as
tracked history before pushing. MP4s require review and an exact fingerprint in
the publication guard. Use a GitHub username, its noreply email and UTC commit
timestamps. Never copy a running installation's profile into the repository.

Keep hardware status honest: developed and tested on Jetson Orin Nano 8GB;
other targets have the verification level stated in their device guides.
