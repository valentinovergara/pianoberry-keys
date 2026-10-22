#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
  echo "Run: sudo bash scripts/install.sh" >&2; exit 1
fi
if [[ $(uname -s) != Linux ]] || ! command -v apt-get >/dev/null; then
  echo "Requires Raspberry Pi OS / Debian with systemd" >&2; exit 1
fi
SOURCE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
apt-get update
apt-get install -y --no-install-recommends python3 python3-mido python3-rtmidi libfluidsynth3 fluid-soundfont-gm alsa-utils
if ! id ivorybox >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin ivorybox
fi
usermod -a -G audio ivorybox
install -d /opt/ivorybox /etc/ivorybox
cp -R "$SOURCE/ivorybox" /opt/ivorybox/
chown -R root:root /opt/ivorybox
if [[ ! -e /etc/ivorybox/config ]]; then
  install -m 644 "$SOURCE/config.example" /etc/ivorybox/config
fi
install -m 644 "$SOURCE/ivorybox.service" /etc/systemd/system/ivorybox.service
systemctl daemon-reload
systemctl enable ivorybox.service
systemctl restart ivorybox.service
sleep 2
systemctl --no-pager status ivorybox.service
