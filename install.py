#!/usr/bin/env python3
"""User-only Jetson Cast setup. Python 3.10+, no pip/npm/sudo required."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE / 'src'))
from lite import asset_names, player_defaults, select_lite
VERSION = '0.1.0'
UPSTREAM = '2.0.1'
RELEASES = {
    'aarch64': ('arm64', '70e2489592ecb2dfe9b334fe6a7a496e9d712627f417506f59e3a88477320e6a'),
    'x86_64': ('x64', '21a6ffb350d0464bcf4452c2a56c59dda4e1062b1fc057f151b9762aa2a117e9'),
}
MARKER = 'jetson-cast-managed-v1'
DEVICE_PROFILES = json.loads((SOURCE / 'devices/profiles.json').read_text(encoding='utf-8'))


def select_device(requested, machine, userspace_bits, os_release, model):
    architecture = {'arm64': 'aarch64', 'amd64': 'x86_64'}.get(machine.lower(), machine.lower())
    if architecture not in RELEASES or userspace_bits != 64:
        raise ValueError('Use a 64-bit Ubuntu installation on ARM64 or Intel/AMD x86-64. '
                         '32-bit operating systems and CPUs are unsupported. See devices/README.md.')
    version = os_release.get('VERSION_ID')
    if os_release.get('ID') != 'ubuntu' or version not in ('22.04', '24.04'):
        raise ValueError('Use Ubuntu 22.04 or 24.04 LTS with a desktop supported by your hardware. '
                         'See devices/README.md for the available setups.')

    detected = next((key for key, profile in DEVICE_PROFILES.items()
                     if profile['architecture'] == architecture and profile.get('model_contains')
                     and profile['model_contains'].casefold() in model.casefold()), None)
    default = 'x86-pc' if architecture == 'x86_64' else 'generic-arm64'
    key = (detected or default) if requested == 'auto' else requested
    profile = DEVICE_PROFILES[key]
    guide = f'devices/{key}/README.md'
    if profile['architecture'] != architecture:
        raise ValueError(f"{profile['label']} requires {profile['architecture']}. "
                         'Omit --device to use the detected architecture, or run python3 install.py devices.')
    if detected and key not in (detected, default):
        raise ValueError(f"This computer matches {DEVICE_PROFILES[detected]['label']}, not {profile['label']}. "
                         f'Omit --device or use --device {detected}.')
    target = detected or key  # Generic ARM64 cannot bypass a known board's Ubuntu requirement.
    if version not in DEVICE_PROFILES[target]['ubuntu']:
        allowed = ' or '.join(DEVICE_PROFILES[target]['ubuntu'])
        raise ValueError(f"{DEVICE_PROFILES[target]['label']} needs Ubuntu {allowed} LTS for this setup. "
                         f'See devices/{target}/README.md.')
    return key, architecture, version, guide


def devices(args):
    print('Choose the guide for the computer connected to your TV:')
    for key, profile in DEVICE_PROFILES.items():
        print(f"  {key}: {profile['label']} ({profile['evidence']}) — devices/{key}/README.md")
    print('The installer detects the CPU and known ARM boards automatically. Use --device ID to choose a guide.')
    print('Opt-in Pi 3 / Zero 2 W experiment: --lite (Raspberry Pi OS ARM64); see experiments/pi-lite/README.md. Not hardware-validated.')


def desktop_session(env):
    if env.get('WAYLAND_DISPLAY'):
        return 'Wayland'
    if env.get('DISPLAY'):
        return 'X11'
    return None


def preflight(args):
    try:
        os_release = platform.freedesktop_os_release()
    except OSError:
        os_release = {}
    model = ''
    for path in ('/proc/device-tree/model', '/sys/firmware/devicetree/base/model'):
        try:
            model = Path(path).read_text(encoding='utf-8', errors='replace').strip('\0\n')
            break
        except OSError:
            pass
    lite = getattr(args, 'lite', False)
    if lite:
        label = select_lite(platform.machine(), struct.calcsize('P') * 8, os_release, model)
        architecture, version, guide = 'aarch64', os_release['VERSION_ID'], 'experiments/pi-lite/README.md'
        profile = {'label': label, 'evidence': 'Experimental; no physical casting, audio or memory measurements'}
        os_name = 'Debian / Raspberry Pi OS'
    else:
        key, architecture, version, guide = select_device(args.device, platform.machine(), struct.calcsize('P') * 8,
                                                         os_release, model)
        profile = DEVICE_PROFILES[key]
        os_name = 'Ubuntu'
    display = desktop_session(os.environ)
    ldd = shutil.which('ldd')
    print(f"Device: {profile['label']} | {os_name} {version} | {architecture}")
    print(f"Verification: {profile['evidence']}. Guide: {guide}")
    if display == 'Wayland':
        print('Desktop: Wayland detected. X11 is the tested session; try it if fullscreen or idle mode misbehaves.')
    elif display == 'X11':
        print('Desktop: X11 display detected.')
    else:
        print('Desktop: no display detected. Sign in on the TV and open a terminal there to launch the receiver.')
    if version == '24.04':
        print('Ubuntu 24.04 startup is unverified; see docs/compatibility.md if AppArmor blocks Electron.')
    if not ldd:
        print('Dependency checker (ldd): missing. Ask your desktop administrator to restore the libc-bin package.')
    if shutil.which('pactl'):
        print('Audio control (pactl): available.')
    else:
        print('Audio control (pactl): missing. Use the desktop sound settings, or ask for pulseaudio-utils to enable per-app routing.')
    return architecture, display, ldd


def missing_runtime_libraries(ldd, executable):
    """Check the exact executable only after it comes from the pinned, verified archive."""
    result = subprocess.run([ldd, str(executable)], capture_output=True, text=True, timeout=15,
                            env={**os.environ, 'LC_ALL': 'C'})
    missing = sorted({line.split(' => ', 1)[0].strip() for line in result.stdout.splitlines()
                      if ' => not found' in line})
    if not missing and (result.returncode or 'not found' in result.stderr):
        raise ValueError('Could not check the runtime libraries. Ask your desktop administrator to check '
                         'the desktop packages and CPU architecture; see docs/compatibility.md.')
    return missing


def locations(lite=False):
    home = Path.home().resolve()
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share')).expanduser().resolve()
    config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config')).expanduser().resolve()
    if any(c in str(home) + str(data) + str(config) for c in '\n\r\0'):
        raise ValueError('Control characters in home paths are unsupported')
    slug = 'jetson-cast-lite' if lite else 'jetson-cast'
    return data / slug, home / '.local/bin' / slug, data / 'applications' / (slug + '.desktop'), config / 'autostart' / (slug + '.desktop')


def write_private(file, text):
    reject_symlinks(file)
    file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if file.is_symlink():
        raise ValueError('Refusing symlink: ' + file.name)
    descriptor, name = tempfile.mkstemp(prefix='.' + file.name + '-', dir=file.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(text.encode('utf-8') if isinstance(text, str) else text)
        temporary.replace(file)
    finally:
        temporary.unlink(missing_ok=True)


def reject_symlinks(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError('Refusing symlink in managed path')


def check_managed_tree(base):
    reject_symlinks(base)
    for name in ('src', 'ambient', 'profile', 'runtime', 'settings.json', 'INSTALLATION'):
        target = base / name
        reject_symlinks(target)
        if target.is_dir() and name in ('src', 'ambient'):
            if any(p.is_symlink() for p in target.rglob('*')):
                raise ValueError('Refusing symlink inside managed application files')


def validate_settings(config):
    if config.get('edition', 'standard') not in ('standard', 'lite'):
        raise ValueError('Unknown installation edition')
    name = config.get('name', '')
    if not isinstance(name, str) or not 1 <= len(name) <= 48 or any(ord(c) < 32 for c in name):
        raise ValueError('Receiver name must be 1–48 printable characters')
    seconds = config.get('rotation_seconds', 300)
    if type(seconds) is not int or not 30 <= seconds <= 86400:
        raise ValueError('Background interval must be 30–86400 seconds')
    sink = config.get('audio_sink', '')
    if not isinstance(sink, str) or any(ord(c) < 32 for c in sink):
        raise ValueError('Invalid audio output')
    return config


def choose_settings(existing=None, interactive=True):
    config = dict(existing or {'name': 'Jetson Cast', 'rotation_seconds': 300, 'audio_sink': '', 'input_switch': False})
    if not interactive:
        return validate_settings(config)
    config['name'] = input('Name shown on your phone [' + config['name'] + ']: ').strip() or config['name']
    minutes = '' if config.get('edition') == 'lite' else input('Change idle background every how many minutes [5]: ').strip()
    if minutes:
        config['rotation_seconds'] = int(minutes) * 60
    try:
        from audio import query
        sinks = query('sinks')
    except (OSError, ValueError, subprocess.SubprocessError):
        sinks = []
    print('\nTV sound: 0 = follow your desktop audio output (safe default)')
    for i, sink in enumerate(sinks, 1):
        print(f"  {i} = {sink.get('description', sink['name'])}")
    choice = input('Choose the TV HDMI/DisplayPort output, or Enter for 0: ').strip() or '0'
    if not choice.isdigit() or not 0 <= int(choice) <= len(sinks):
        raise ValueError('Choose one of the listed outputs')
    config['audio_sink'] = sinks[int(choice) - 1]['name'] if int(choice) else ''
    return validate_settings(config)


def extract_checked(archive, destination):
    """Extract regular files/directories only, without archive owners or special bits."""
    with tarfile.open(archive, 'r:gz') as tar:
        entries = tar.getmembers()
        if sum(m.size for m in entries) > 2 * 1024**3:
            raise ValueError('Archive is unexpectedly large')
        for member in entries:
            target = destination / member.name
            if member.name.startswith('/') or '\\' in member.name or '..' in Path(member.name).parts:
                raise ValueError('Unsafe archive path')
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError('Archive escaped staging directory')
            if not (member.isfile() or member.isdir()):
                raise ValueError('Unsupported archive link or special file')
        for member in entries:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
            else:
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with tar.extractfile(member) as src, target.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)


def download(file, architecture):
    suffix, expected = RELEASES[architecture]
    url = f'https://github.com/shy1132/VacuumTube/releases/download/v{UPSTREAM}/VacuumTube-{suffix}.tar.gz'
    request = urllib.request.Request(url, headers={'User-Agent': 'Jetson-Cast-Installer/' + VERSION})
    digest, size = hashlib.sha256(), 0
    with urllib.request.urlopen(request, timeout=60) as response, file.open('xb') as out:
        if not response.geturl().startswith('https://'):
            raise ValueError('Download redirected away from HTTPS')
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > 512 * 1024**2:
                raise ValueError('Download exceeds size limit')
            digest.update(chunk)
            out.write(chunk)
    if digest.hexdigest() != expected:
        raise ValueError('Upstream SHA256 mismatch; nothing installed')


def owned(path):
    if not path.is_file() or any(p.is_symlink() for p in (path, *path.parents)):
        return False
    return any(line in (MARKER, '# ' + MARKER, 'X-Jetson-Cast-Managed=' + MARKER)
               for line in path.read_text().splitlines())


def desktop_text(base, lite=False):
    argument = str(base / 'src/launch.py').replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    return f'''[Desktop Entry]
Type=Application
Name={'Jetson Cast Lite' if lite else 'Jetson Cast'}
Comment=YouTube on your TV, controlled from your phone
Exec=python3 "{argument}"
Icon=video-display
Terminal=false
Categories=AudioVideo;Video;
StartupWMClass=VacuumTube
X-Jetson-Cast-Managed={MARKER}
'''


def install(args):
    architecture, display, ldd = preflight(args)
    lite = getattr(args, 'lite', False)
    base, launcher, desktop, autostart = locations(lite)
    check_managed_tree(base)
    if (base / 'runtime').exists():
        if not owned(base / 'INSTALLATION') or not owned(launcher) or not (base / 'settings.json').is_file():
            raise ValueError('Incomplete or unmanaged installation; inspect it before reinstalling')
        if not args.dry_run:
            print('Already installed. Run python3 install.py configure or doctor' + (' with --lite.' if lite else '.'))
            return
    if base.exists() and not owned(base / 'INSTALLATION'):
        raise ValueError('Destination already exists and is not managed by Jetson Cast')
    for target in (launcher, desktop, autostart):
        if target.is_symlink() or (target.exists() and not owned(target)):
            raise ValueError('Refusing to overwrite an existing launcher: ' + target.name)
    if args.dry_run:
        print(f'Plan: VacuumTube {UPSTREAM} for {architecture}; isolated user profile; no root, DNS, firewall or Docker changes.')
        if lite:
            print('Lite: separate app/profile/launchers; low-memory mode; H.264 filter; no ambient assets or Jet. Hardware untested.')
        return
    if not display and not args.non_interactive:
        raise ValueError('Open a terminal on your TV desktop, or use --non-interactive to install remotely and launch there later.')
    if not ldd:
        raise ValueError('The runtime dependency check needs ldd. Restore libc-bin and rerun setup.')
    config = json.loads((base / 'settings.json').read_text()) if (base / 'settings.json').exists() else None
    if lite and config is None:
        config = {'name': 'Jetson Cast Lite', 'rotation_seconds': 300, 'audio_sink': '', 'input_switch': False, 'edition': 'lite'}
    config = choose_settings(config, not args.non_interactive)
    start_at_login = args.autostart
    if not args.non_interactive and not start_at_login:
        start_at_login = input('Start Jetson Cast when you log in? [y/N]: ').lower() == 'y'
    base.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    print(f'\nDownloading and verifying VacuumTube {UPSTREAM} for {architecture}…')
    with tempfile.TemporaryDirectory(prefix='.jetson-cast-stage-', dir=base.parent) as temporary:
        stage = Path(temporary)
        archive = stage / 'upstream.tar.gz'
        download(archive, architecture)
        expanded = stage / 'expanded'
        expanded.mkdir()
        extract_checked(archive, expanded)
        binaries = list(expanded.rglob('vacuumtube'))
        binaries = [p for p in binaries if p.is_file() and (p.parent / 'resources/app.asar').is_file()]
        if len(binaries) != 1:
            raise ValueError('Upstream runtime layout has changed')
        runtime = binaries[0].parent
        missing = missing_runtime_libraries(ldd, binaries[0])
        if missing:
            raise ValueError('Missing desktop libraries: ' + ', '.join(missing) + '. '
                             'Ask your desktop administrator to install the packages for your OS that provide them, then retry. '
                             'See docs/compatibility.md.')
        from patch import customize
        app = runtime / 'resources/app.asar'
        app.write_bytes(customize(app.read_bytes(), SOURCE / 'src', lite=lite))
        base.mkdir(mode=0o700, exist_ok=True)
        base.chmod(0o700)
        write_private(base / 'INSTALLATION', MARKER + '\n' + VERSION + '\n')
        for file in (SOURCE / 'src').iterdir():
            if lite and file.name in ('ambient.js', 'input-intent.js'):
                continue
            if file.suffix in ('.py', '.js'):
                write_private(base / 'src' / file.name, file.read_bytes())
        if not lite:
            (base / 'ambient').mkdir(exist_ok=True, mode=0o700)
        for file in asset_names(lite):
            write_private(base / 'ambient' / file, (SOURCE / 'assets' / file).read_bytes())
        profile = base / 'profile'
        profile.mkdir(mode=0o700, exist_ok=True)
        reject_symlinks(profile / 'config.json')
        if not (profile / 'config.json').exists():
            write_private(profile / 'config.json', json.dumps(player_defaults(lite), indent=2) + '\n')
        write_private(base / 'settings.json', json.dumps(config, indent=2) + '\n')
        wrapper = '#!/usr/bin/env python3\n# ' + MARKER + '\nimport os\nos.execvp("python3", ["python3", ' + repr(str(base / 'src/launch.py')) + '])\n'
        write_private(launcher, wrapper)
        launcher.chmod(0o700)
        write_private(desktop, desktop_text(base, lite))
        if start_at_login:
            write_private(autostart, desktop_text(base, lite))
        elif owned(autostart):
            autostart.unlink()
        # Commit runtime last: an interrupted setup remains safely retryable.
        runtime.rename(base / 'runtime')
    label = 'Jetson Cast Lite' if lite else 'Jetson Cast'
    slug = 'jetson-cast-lite' if lite else 'jetson-cast'
    print(f'\nInstalled. Open {label} from your applications menu, or run ~/.local/bin/{slug}')
    print('On the TV, complete YouTube first-run setup. On your phone: YouTube → Cast → ' + config['name'])
    print('Login startup is ' + ('enabled.' if start_at_login else 'off.') + ' Automatic login is not changed.')
    print('For sound or discovery help: python3 install.py doctor' + (' --lite' if lite else ''))


def configure(args):
    lite = getattr(args, 'lite', False)
    base, _, _, autostart = locations(lite)
    check_managed_tree(base)
    if not owned(base / 'INSTALLATION'):
        raise ValueError('Install Jetson Cast first')
    config = choose_settings(json.loads((base / 'settings.json').read_text()), True)
    write_private(base / 'settings.json', json.dumps(config, indent=2) + '\n')
    if input('Start at desktop login? [y/N]: ').lower() == 'y':
        if autostart.exists() and not owned(autostart):
            raise ValueError('Refusing to replace an unrelated autostart entry')
        write_private(autostart, desktop_text(base, lite))
    elif owned(autostart):
        autostart.unlink()
    print('Saved. Close and reopen Jetson Cast to apply.')


def doctor(args):
    print('Jetson Cast doctor — no tokens, IP addresses, history or account data collected')
    _, _, ldd = preflight(args)
    base, _, _, autostart = locations(getattr(args, 'lite', False))
    check_managed_tree(base)
    managed = owned(base / 'INSTALLATION')
    executable = base / 'runtime/vacuumtube'
    installed = managed and executable.is_file() and not executable.is_symlink()
    print('Installed:', installed, '| Login startup:', owned(autostart))
    if installed and ldd:
        missing = missing_runtime_libraries(ldd, executable)
        print('Missing desktop libraries:', ', '.join(missing) if missing else 'none reported')
    elif not installed:
        print('Runtime libraries: checked after the verified download during installation.')
    print('If discovery fails: use the same trusted LAN, disable Wi-Fi client isolation, reopen the phone Cast picker.')
    print('If sound fails: turn on/select the TV, run configure, select its HDMI output, reopen the receiver.')
    print('If Electron reports a sandbox error: see docs/compatibility.md; do not disable the sandbox.')


def uninstall(args):
    base, launcher, desktop, autostart = locations(getattr(args, 'lite', False))
    if base.is_symlink() or not owned(base / 'INSTALLATION'):
        raise ValueError('No managed installation found; nothing removed')
    if not args.yes and input('Close Jetson Cast first. Remove its runtime and launchers, keeping profile/settings? [y/N]: ').lower() != 'y':
        return
    for file in (launcher, desktop, autostart):
        if owned(file):
            file.unlink()
    for name in ('runtime', 'src', 'ambient'):
        target = base / name
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            if target.resolve().parent != base.resolve():
                raise ValueError('Unsafe uninstall path')
            shutil.rmtree(target)
    print('Removed application and launchers. Private profile/settings retained in your user data directory.')
    print('You may reinstall using python3 install.py' + (' --lite.' if getattr(args, 'lite', False) else '.') + ' No other service or system setting was changed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs='?', choices=['install', 'configure', 'doctor', 'devices', 'uninstall'], default='install')
    parser.add_argument('--device', choices=['auto', *DEVICE_PROFILES], default='auto',
                        help='select an optional device guide for install or doctor (default: auto)')
    parser.add_argument('--non-interactive', action='store_true', help='use safe defaults; autostart only with --autostart')
    parser.add_argument('--autostart', action='store_true', help='opt in to desktop-login startup')
    parser.add_argument('--dry-run', action='store_true', help='show install plan without downloading or changing files')
    parser.add_argument('--yes', action='store_true', help='confirm uninstall while retaining profile/settings')
    parser.add_argument('--lite', action='store_true', help='isolated Pi 3 / Zero 2 W experiment on Raspberry Pi OS ARM64; hardware untested')
    args = parser.parse_args()
    if args.lite and args.device != 'auto':
        parser.error('--lite detects its Pi board; do not combine it with --device')
    if args.dry_run and args.command != 'install':
        parser.error('--dry-run is for install; use doctor for a read-only check')
    if args.device != 'auto' and args.command not in ('install', 'doctor'):
        parser.error('--device is for install or doctor')
    if args.command == 'devices':
        devices(args)
        return 0
    if sys.platform != 'linux' or sys.version_info < (3, 10):
        parser.error('Use Linux with Python 3.10 or newer')
    if os.geteuid() == 0:
        parser.error('Run as your desktop user, without sudo')
    try:
        globals()[args.command](args)
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
        print('Setup stopped:', error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
