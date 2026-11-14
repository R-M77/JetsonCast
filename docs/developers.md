# Build with JetsonCast

Clone the repo and open it in your coding assistant. Project skills are included:

| Assistant | Invoke | Repository location |
| --- | --- | --- |
| Codex | `$jetsoncast` | `.agents/skills/jetsoncast/` |
| Claude Code | `/jetsoncast` | `.claude/skills/jetsoncast/` |

Try: **“Check whether this computer can run JetsonCast, then walk me through setup.”**
Or: **“Help add a device guide and validate it without touching my live receiver.”**

Start a new session in this checkout if the skill is missing. Repository skills
must be enabled and trusted by your client. These skills guide existing local
commands; they install no MCP server, background service, API key, or remote-control
endpoint. [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
· [Claude Code project skills](https://code.claude.com/docs/en/skills#choose-where-skills-load).

Validation: Codex's local skill loader discovered and enabled `jetsoncast` at
repository scope. Both skill files pass schema validation; Claude Code's live
skill menu has not been exercised.

## Where to contribute

| Area | Start here |
| --- | --- |
| Device support and setup | `devices/`, `install.py` |
| Screensavers and Jet | `src/ambient.js`, `assets/` |
| Runtime patch and launch | `src/patch.py`, `src/launch.py` |
| HDMI audio | `src/audio.py` |
| Experimental TV input switching | `addons/` |

Run the checks in [Contributing](../CONTRIBUTING.md). Hardware reports are especially
helpful: OS, architecture, desktop session, and discovery/playback/audio results.
Keep account names, addresses, profiles and unredacted logs out of reports.
