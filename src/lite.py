"""Opt-in Pi experiment. No host changes or hardware performance claims."""


def select_lite(machine, userspace_bits, os_release, model):
    if machine.lower() not in ('aarch64', 'arm64') or userspace_bits != 64:
        raise ValueError('Lite requires 64-bit ARM64 userspace; original Pi Zero and 32-bit OS images are unsupported.')
    if os_release.get('ID') not in ('debian', 'raspbian') or os_release.get('VERSION_ID') not in ('12', '13'):
        raise ValueError('Lite targets Raspberry Pi OS 64-bit Bookworm (12) or Trixie (13). See experiments/pi-lite/README.md.')
    if model.startswith('Raspberry Pi Zero 2 W '):
        return 'Pi Zero 2 W (512MB; high-risk experiment)'
    if model.startswith(('Raspberry Pi 3 Model B ', 'Raspberry Pi 3 Model A Plus ')):
        return 'Pi 3 (experimental; B/B+ preferred over 512MB A+)'
    raise ValueError('Lite is an opt-in experiment for Pi Zero 2 W and Pi 3 only. Use the standard setup for other hardware.')


def player_defaults(lite=False):
    config = {'adblock': True, 'fullscreen': True, 'device_discoverability': True, 'auto_update': False}
    if lite:
        config.update({
            'low_memory_mode': True,
            'h264ify': True,
            'h264ify_disable_webm': True,
            'h264ify_disable_vp8': True,
            'h264ify_disable_vp9': True,
            'h264ify_disable_av1': True,
            'hardware_decoding': True,
            'unlock_resolution': False,
            'remove_super_resolution': True,
            'controller_support': False,
            'touch_overlay': False,
            'sponsorblock': False,
            'dearrow': False,
            'dislikes': False,
        })
    return config


def asset_names(lite=False):
    return () if lite else ('aurora-lake.gif', 'golden-coast.gif', 'moonlit-meadow.gif', 'orbital-dawn.gif',
                           'jet-open.png', 'jet-blink.png', 'jet-actions.png')
