#!/bin/bash
set -euo pipefail
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
exec >> "$BOOT/IVORYBOX-INSTALACION-OFFLINE.txt" 2>&1
trap 'echo "ERROR en línea $LINENO; reintento automático"; sync' ERR
echo "Instalación offline: $(date -Is)"
# Use an isolated local apt repository: no external source or DNS is required.
echo 'deb [trusted=yes] file:/opt/ivorybox-offline/repo ./' > /opt/ivorybox-offline/local.list
mkdir -p /opt/ivorybox-offline/lists/partial
OPTS=(-o Dir::Etc::sourcelist=/opt/ivorybox-offline/local.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/opt/ivorybox-offline/lists -o Acquire::Languages=none)
export DEBIAN_FRONTEND=noninteractive
apt-get "${OPTS[@]}" update
apt-get "${OPTS[@]}" install -y --no-install-recommends python3-mido python3-rtmidi libfluidsynth3 fluid-soundfont-gm
if ! id ivorybox >/dev/null 2>&1; then useradd --system --no-create-home --shell /usr/sbin/nologin ivorybox; fi
usermod -a -G audio ivorybox
install -d /opt/ivorybox /etc/ivorybox
cp -R /opt/ivorybox-source/ivorybox/ivorybox /opt/ivorybox/
chown -R root:root /opt/ivorybox
chmod -R a+rX /opt/ivorybox
cat > /etc/ivorybox/config <<'CONFIG'
AUDIO_DEVICE=plughw:CARD=Headphones,DEV=0
SOUNDFONT=/usr/share/sounds/sf2/FluidR3_GM.sf2
GAIN=0.5
PERIOD=256
MIDI_MATCH=""
CONFIG
install -m 644 /opt/ivorybox-source/ivorybox/ivorybox.service /etc/systemd/system/ivorybox.service
systemctl daemon-reload
amixer -c Headphones sset PCM 80% || true
cd /opt/ivorybox
runuser -u ivorybox -- /usr/bin/python3 -m ivorybox --list-midi
# Play a short piano confirmation before handing audio to the live MIDI service.
systemctl stop ivorybox || true
runuser -u ivorybox -- /usr/bin/python3 - <<'PY'
from ivorybox.engine import Synth
import time
s=Synth('/usr/share/sounds/sf2/FluidR3_GM.sf2','plughw:CARD=Headphones,DEV=0',0.5,256)
try:
 for note in (60,64,67,72):
  s.send('noteon',0,note,85);time.sleep(.35);s.send('noteoff',0,note)
 time.sleep(.5)
finally:s.close()
PY
systemctl enable ivorybox
systemctl restart ivorybox
sleep 5
systemctl is-active --quiet ivorybox
systemctl status ivorybox --no-pager -l
journalctl -u ivorybox -b -n 40 --no-pager
touch /opt/ivorybox-offline/complete
systemctl disable ivorybox-offline.service
echo 'INSTALACION_COMPLETA — Piano listo para tocar.'
sync
