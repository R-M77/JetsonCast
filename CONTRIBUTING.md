# Contributing

Use your GitHub username and GitHub-provided `users.noreply.github.com` commit
email. This repository's publication guard rejects personal email addresses
and non-UTC commit timestamps in history. Author and committer names must match
the username in their noreply address. Set `GIT_AUTHOR_DATE` and
`GIT_COMMITTER_DATE` to UTC when committing (for example,
`GIT_AUTHOR_DATE="$(date -u +%FT%TZ)" GIT_COMMITTER_DATE="$(date -u +%FT%TZ)" git commit`).
Use local merges with compliant metadata; GitHub-generated merge commits may
fail the same guard. Do not attach account profiles, private network configuration or
unredacted desktop screenshots. See [repeatable validation](docs/validation.md).

Project skills for Codex and Claude Code are included. [Start here](docs/developers.md).

```bash
python3 -m unittest discover -s tests -v
node tests/test_ambient.cjs
python3 scripts/privacy_check.py --history
```

For a bug report, include the Ubuntu version, CPU architecture, desktop session type, and the shortest sequence that reproduces the issue. Include relevant output from `python3 install.py doctor` after removing account, network, and device details. Use the [private reporting guidance](SECURITY.md#report-a-vulnerability) for security findings.

For a change to the installer or launcher, test it from a fresh checkout with a regular user account. Record which of install, launch, configuration, doctor, and uninstall you exercised. For receiver changes, describe whether phone discovery, real playback, and audio were tested on hardware. Update the [compatibility table](docs/compatibility.md#host-and-display) if your change affects tested behavior.

Have a spare Pi 3 or Zero 2 W? The [Lite experiment](experiments/pi-lite/)
needs physical casting, audio and memory results. Keep its status experimental
until those checks pass; fixture-based installer tests do not establish playback support.

Keep test data synthetic and contributions focused on the Jetson Cast installer, setup, and TV integration. For issues reproducible in stock VacuumTube, use the [VacuumTube issue tracker](https://github.com/shy1132/VacuumTube/issues).
