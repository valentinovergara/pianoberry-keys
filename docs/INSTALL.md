# Installation and troubleshooting

## Standard installation

1. Install Raspberry Pi OS Lite 64-bit on microSD or supported USB storage. Bookworm is the tested base.
2. Configure a user and, if needed, SSH using Raspberry Pi Imager. This project's standard installer does not create a remote login.
3. Connect the Q49 by USB, speakers/headphones to the Pi jack, and an internet connection.
4. Clone the repository and run `sudo bash scripts/install.sh` from its root.
5. Check `journalctl -u ivorybox.service -b`. Look for the selected MIDI input and listen for the arpeggio.

The installer needs root privileges and a network connection to install Debian packages. Runtime uses an unprivileged audio-group account. Installing packages successfully does not by itself prove that audio is audible.

## Audio device and volume

Run `aplay -l` and `aplay -L`. The tested onboard jack is `plughw:CARD=Headphones,DEV=0`; use the actual card identifier rather than a numeric card index that can change. Set `AUDIO_DEVICE` in `/etc/ivorybox/config` accordingly. For HDMI or USB audio, use the name shown by your hardware.

To test the jack independently of the synthesizer:

```bash
sudo systemctl stop ivorybox.service
amixer -c Headphones sset PCM 80%
speaker-test -D plughw:CARD=Headphones,DEV=0 -c 2 -t sine
# Stop the tone with Ctrl+C, then restore the instrument:
sudo systemctl start ivorybox.service
```

Change the card name if needed. Test with powered speakers or headphones and low external volume. If another application owns the output, use an available device or a dedicated Lite installation. A service without a desktop login may not be able to use a session-only `default` device. Audio-interface hot-unplugging may require a service restart; automatic reconnection is implemented for MIDI.

## No controller appears

```bash
cd /opt/ivorybox
sudo -u ivorybox /usr/bin/python3 -m ivorybox --list-midi
aconnect -l
lsusb
```

Check a USB data cable and adequate power. Try a direct USB connection or powered hub. Set `MIDI_MATCH="Q49"` to wait specifically for that name; this prevents fallback to another controller. MIDI Through is excluded automatically. Other virtual inputs can still be selected, so use a filter on shared machines.

## Ethernet connected but downloads fail

A direct cable to a Mac does not provide internet automatically. On macOS, enable Internet Sharing **from Wi-Fi to the Ethernet adapter physically connected to the Pi**. Keep the Mac awake and sharing enabled during installation. Alternatively connect the Pi directly to a router that provides DHCP and internet.

On the Pi, inspect `ip -brief address`, `ip route`, and `getent hosts deb.debian.org`. An interface with only a link-local address may not have usable internet. Resolve connectivity before repeatedly reinstalling. Offline recovery scripts are documented in [deploy/usb](../deploy/usb/README.md).

## Crackles or latency

Try `PERIOD=512`, restart, and compare. Close CPU-heavy processes and check power and temperature. The ALSA driver may negotiate a larger period than requested; that warning is not necessarily a startup failure. This project does not configure a real-time kernel, and Bluetooth audio is outside the tested configuration.

## Upgrade and roll back

Back up `/etc/ivorybox/config`, select the desired Git release tag, and rerun the installer. Existing configuration is preserved. To roll back, check out a previous tag and reinstall. The Linux module, service account, service name, and paths remain `ivorybox` after the public rename to Orphic Keys.

## Remove

```bash
sudo systemctl disable --now ivorybox.service
sudo rm /etc/systemd/system/ivorybox.service
sudo systemctl daemon-reload
sudo rm -r /opt/ivorybox
```

Configuration, installed packages, and the service account are left in place. Remove those manually if unused. Optional SSH maintenance access, if separately provisioned, must also be revoked separately. Shut down the Pi with `sudo poweroff` before disconnecting power.
