# Security

## Release status

The pinned VacuumTube 2.1.1 Linux ARM64 and x86-64 downloads contain Electron 45.3.2. This includes the fix for [GHSA-jr5w-w6x2-84p9](https://github.com/advisories/GHSA-jr5w-w6x2-84p9). Earlier JetsonCast installations using VacuumTube 2.0.1 need the [runtime upgrade](docs/compatibility.md#upgrade-an-existing-installation). See the [validation record](docs/validation.md) for the hardware checks completed on each version.

## Local network access

VacuumTube's DIAL discovery lets other devices on the LAN find the receiver. The local discovery and launch interface does not require each device to authenticate, so run Jetson Cast on a trusted network and keep its ports off the public internet. Leave router port forwarding off. You can turn off **Device Discoverability** in VacuumTube settings to disable discovery.

VacuumTube uses Electron to load YouTube and can contact third-party services for optional features such as SponsorBlock. The installer downloads a pinned upstream release and checks its SHA-256 digest before installing it. Security still depends on upstream code, the local operating system, and the services the application contacts. [VacuumTube settings](https://github.com/shy1132/VacuumTube/blob/v2.1.1/README.md#settings)

Jetson Cast uses a dedicated local app profile. Treat its cookies, settings, and any optional TV helper configuration as private. Keep credentials and device configuration local, and redact them from diagnostics, recordings, and issue reports.

VacuumTube 2.1.1's renderer uses `sandbox: false` and `contextIsolation: false`
for its privileged YouTube integrations. This package preserves that upstream
architecture; it does not provide browser-grade isolation from the web content
it loads. The launcher does not add a global `--no-sandbox` flag and excludes
upstream Steam game mode, but this does not remove the renderer risk. Prefer a
dedicated, unprivileged desktop account for a shared TV. No software can promise
zero vulnerabilities. The pinned runtime is not automatically updated: monitor
upstream security releases and reassess the pin before a public launch.

Run `python3 scripts/privacy_check.py --history` before publishing. The guard
checks tracked files, image metadata and Git history for common private-data
patterns; it is a supplement to human review, not a guarantee. Installed profiles,
settings and TV identifiers belong outside the checkout. Do not publish logs or
screenshots without inspecting them.

Passing the guard does not certify every copy hosted by GitHub. Its history scan
covers locally reachable Git objects; old commits removed from branches may
still be accessible by their object IDs. Before changing repository visibility,
also review hosted releases, attachments, Actions logs and artifacts, and any
known superseded commits. Rewriting history or force-pushing alone does not
guarantee removal of sensitive hosted objects. Resolve any retained private data
with GitHub's removal process, or publish a separately reviewed clean repository.

## Report a vulnerability

Contact a maintainer privately with the affected version, reproduction steps, and the impact. If you only have access to the issue tracker, ask for a private reporting channel and keep exploit details and personal information out of the issue.
