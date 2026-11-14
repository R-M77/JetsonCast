#!/usr/bin/env python3
"""Local TV input automation. Does not power the TV or launch receiver apps."""
import argparse
import ipaddress
import os
import json
import logging
import pathlib
import queue
import socket
import threading
import tempfile
import time
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import pychromecast

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--config', type=pathlib.Path, default=pathlib.Path(os.environ.get('XDG_DATA_HOME', pathlib.Path.home() / '.local/share')) / 'jetson-cast/state/config.json')
args = parser.parse_args()
BASE = args.config.resolve().parent
CONFIG = json.loads(args.config.read_text())
SERVICE = 'urn:samsung.com:service:MainTVAgent2:1'
MAX_TV_XML_BYTES = 256 * 1024
SOURCES = {key: (CONFIG['sources'][key]['name'], str(CONFIG['sources'][key]['id'])) for key in ('jetson', 'chromecast')}

def lan_address(host):
    try:
        ip = ipaddress.IPv4Address(host)
        return ip.is_private and not (ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified)
    except (ValueError, TypeError):
        return False

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('TV redirect rejected')

HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

def checked_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'http' or not lan_address(parsed.hostname) or parsed.username or parsed.password:
        raise ValueError('Expected a literal trusted LAN IPv4 HTTP endpoint')
    return url


def read_tv_xml(response):
    data = response.read(MAX_TV_XML_BYTES + 1)
    if len(data) > MAX_TV_XML_BYTES:
        raise ValueError('TV XML response exceeds size limit')
    return ET.fromstring(data)


checked_url(CONFIG['tv_control_url'])
if not lan_address(CONFIG['chromecast']['host']):
    raise ValueError('Chromecast must be a trusted LAN IPv4 address')
EVENTS = queue.Queue()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logging.getLogger('pychromecast').setLevel(logging.ERROR)
logging.getLogger('zeroconf').setLevel(logging.ERROR)


def atomic_json(name, data):
    target = BASE / name
    with tempfile.NamedTemporaryFile(mode='w', dir=BASE, prefix='.intent-', delete=False) as handle:
        temp = pathlib.Path(handle.name)
        json.dump(data, handle)
    try:
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)


class SamsungTV:
    def __init__(self):
        self.control_url = CONFIG['tv_control_url']
        self.last_discovery = 0

    def discover(self):
        self.last_discovery = time.monotonic()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(.4)
        addresses = set()
        try:
            sock.sendto(b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n', ('239.255.255.250', 1900))
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                try:
                    data, peer = sock.recvfrom(8192)
                except socket.timeout:
                    continue
                for line in data.decode(errors='replace').splitlines():
                    if line.lower().startswith('location:'):
                        url = line.split(':', 1)[1].strip()
                        parsed = urllib.parse.urlparse(url)
                        if parsed.scheme == 'http' and parsed.hostname == peer[0] and lan_address(peer[0]):
                            addresses.add(url)
        finally:
            sock.close()
        for url in addresses:
            try:
                with HTTP.open(checked_url(url), timeout=2) as response:
                    root = read_tv_xml(response)
                device = root.find('{*}device')
                if device is None or device.findtext('{*}UDN') != CONFIG['tv_udn']:
                    continue
                for service in device.findall('.//{*}service'):
                    if service.findtext('{*}serviceType') == SERVICE:
                        candidate = checked_url(urllib.parse.urljoin(url, service.findtext('{*}controlURL')))
                        if urllib.parse.urlparse(candidate).hostname != urllib.parse.urlparse(url).hostname:
                            continue
                        self.control_url = candidate
                        return
            except Exception:
                continue

    def call(self, action, args=None):
        # This older Samsung requires the conventional s/u SOAP namespace prefixes.
        params = ''.join(f'<{key}>{escape(str(value))}</{key}>' for key, value in (args or {}).items())
        body = ('<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
                's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
                f'<u:{action} xmlns:u="{SERVICE}">{params}</u:{action}></s:Body></s:Envelope>')
        request = urllib.request.Request(self.control_url, data=body.encode(), headers={
            'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': f'"{SERVICE}#{action}"'})
        try:
            with HTTP.open(request, timeout=3) as response:
                root = read_tv_xml(response)
            reply = list(list(root)[0])[0]
            result = {node.tag.rsplit('}', 1)[-1]: node.text for node in reply}
            if result.get('Result') != 'OK':
                raise RuntimeError('TV rejected ' + action)
            return result
        except Exception:
            if time.monotonic() - self.last_discovery > 60:
                self.discover()
            raise

    def current(self):
        return self.call('GetCurrentExternalSource')['ID']

    def select(self, target):
        source, source_id = SOURCES[target]
        if self.current() != source_id:
            self.call('SetMainTVSource', {'Source': source, 'ID': source_id, 'UiID': '0'})
        # This TV can report its previous/CEC source while an input is settling.
        # Wait for confirmed selection before pausing the other player.
        for _ in range(20):
            if self.current() == source_id:
                return source_id
            time.sleep(.5)
        raise RuntimeError('TV input readback did not match')


class ChromecastMonitor:
    def __init__(self):
        self.cast = None
        self.active = False
        self.last_app = None
        self.initialized = False
        self.connected = False
        self.warmup_until = 0
        self.lock = threading.Lock()

    def supported(self):
        if not self.cast or not self.cast.status:
            return False
        status = self.cast.status
        name = (status.display_name or '').lower()
        return status.app_id in {'9AC194DC', '17608BC8', 'CC1AD845'} or any(n in name for n in ('prime', 'amazon', 'plex'))

    def new_media_status(self, status):
        state = status.player_state
        with self.lock:
            app = self.cast.status.app_id if self.cast and self.cast.status else None
            supported = self.supported()
            playing = supported and state == 'PLAYING'
            trigger = self.initialized and time.monotonic() >= self.warmup_until and playing and (not self.active or app != self.last_app)
            if state != 'BUFFERING':
                self.active = playing
            self.last_app = app
            self.initialized = True
        if trigger:
            EVENTS.put((time.time(), 'chromecast'))

    def new_connection_status(self, status):
        self.connected = status.status == 'CONNECTED'

    def new_cast_status(self, status):
        if self.cast:
            self.new_media_status(self.cast.media_controller.status)

    def pause(self):
        cast = self.cast
        if cast and self.supported() and cast.media_controller.status.player_state in ('PLAYING', 'BUFFERING'):
            try:
                cast.media_controller.pause()
            except Exception:
                logging.warning('Chromecast could not be paused; input remains selected')

    def run(self):
        while True:
            browser = None
            cast = None
            try:
                info = CONFIG['chromecast']
                devices, browser = pychromecast.get_listed_chromecasts(
                    uuids=[uuid.UUID(info['uuid'])], known_hosts=[info['host']],
                    tries=2, retry_wait=2, timeout=4, discovery_timeout=8)
                if not devices:
                    raise RuntimeError('Configured Chromecast not discovered')
                cast = devices[0]
                self.cast = cast
                self.warmup_until = time.monotonic() + 3
                cast.register_connection_listener(self)
                cast.register_status_listener(self)
                cast.media_controller.register_status_listener(self)
                cast.wait(timeout=12)
                cast.media_controller.update_status()
                logging.info('Chromecast status monitoring connected')
                while cast.socket_client.is_alive():
                    time.sleep(5)
            except Exception:
                logging.warning('Chromecast unavailable; retrying without changing the TV')
            finally:
                if cast:
                    try:
                        cast.disconnect(timeout=3)
                    except Exception:
                        pass
                self.cast = None
                self.initialized = False
                self.active = False
                if browser:
                    browser.stop_discovery()
            time.sleep(10)


def pause_jetson():
    atomic_json('jetson-command.json', {'id': str(uuid.uuid4()), 'action': 'pause', 'at': time.time()})


def main():
    tv = SamsungTV()
    tv.discover()
    monitor = ChromecastMonitor()
    threading.Thread(target=monitor.run, daemon=True).start()
    last_intent = None
    intent_path = BASE / 'jetson-intent.json'
    try:
        last_intent = json.loads(intent_path.read_text()).get('id')
    except (OSError, ValueError):
        pass
    last_input = None
    next_poll = 0
    failures = 0
    logging.info('Experimental input automation ready')
    while True:
        now = time.time()
        try:
            intent = json.loads(intent_path.read_text())
            if intent.get('id') != last_intent:
                last_intent = intent.get('id')
                if intent.get('action') == 'play' and 0 <= now - float(intent['at']) < 15:
                    EVENTS.put((float(intent['at']), 'jetson'))
        except (OSError, ValueError, KeyError, TypeError):
            pass
        try:
            at, target = EVENTS.get(timeout=.5)
        except queue.Empty:
            target = None
        if target and time.time() - at < 15:
            try:
                last_input = tv.select(target)
                if target == 'jetson':
                    monitor.pause()
                else:
                    pause_jetson()
                logging.info('Selected configured TV input for %s playback', target)
                failures = 0
                atomic_json('status.json', {'at': time.time(), 'selected': target, 'source_id': last_input})
            except Exception:
                logging.warning('Could not switch TV input; existing playback left alone')
        if time.monotonic() >= next_poll:
            try:
                current = tv.current()
                # Respect manual input changes and Chromecast CEC; do not fight them.
                if last_input and current != last_input:
                    if last_input == SOURCES['jetson'][1]:
                        pause_jetson()
                    elif last_input == SOURCES['chromecast'][1]:
                        monitor.pause()
                last_input = current
                failures = 0
            except Exception:
                failures += 1
            next_poll = time.monotonic() + (5 if failures == 0 else min(60, failures * 10))


if __name__ == '__main__':
    main()
