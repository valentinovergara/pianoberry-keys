# PianoBerry Keys

**A little Raspberry Pi. A keyboard. A world of sound.**

PianoBerry Keys turns a Raspberry Pi 4 Model B into a standalone USB MIDI instrument: power it on, plug in a controller, hear the ready arpeggio, and play.

Built and tested with an **Alesis Q49**, Raspberry Pi 4 B, and the Pi's **3.5 mm audio jack**. Other USB MIDI controllers may work when supported by Linux ALSA; they have not all been tested.

> Previously called **IvoryBox** and briefly **Orphic Keys**. The Python module, Linux service, and configuration paths retain `ivorybox` for compatibility with existing installations.

## Seven voices

| MIDI Program Change | Voice | Character |
|---|---|---|
| **0** | Ivory Piano | Acoustic piano, expressive velocity and sustain |
| **1** | BYTE | Dry square-wave lead inspired by 8-bit games |
| **2** | NEBULA | Warm, slow pad with spacious reverb and chorus |
| **3** | CRYSTAL HARP | Orchestral harp with a quiet music-box shimmer; fantasy-prelude feel |
| **4** | PIXEL QUEST | Monophonic pulse lead, fast attack and short release; NES-inspired |
| **5** | ABYSS | Dark atmosphere pad plus a detuned crystal layer; aquatic ambience |
| **6** | DUSTY KEYS | Filtered electric piano with gentle chorus and reverb; lo-fi chill |

BYTE uses a sampled General MIDI square-wave instrument; it is not a console-chip emulator. NEBULA and ABYSS bloom on held notes and chords. The four newer voices are timbral interpretations inspired by fantasy-game harps, NES melodies, aquatic game ambience, and lo-fi chill. They use only the installed SoundFont, without game recordings, extracted samples, or automatic soundtrack playback. PIXEL QUEST plays only the most recently pressed note on each MIDI channel; choose BYTE for polyphonic square-wave chords. Voices come from the locally installed FluidR3 GM SoundFont. No subscription or cloud audio processing is required.

## What it does

- Starts automatically through systemd without a desktop session.
- Prefers a Q49 when choosing a controller; falls back to another available MIDI input.
- Reconnects after a MIDI controller is unplugged. Only one controller is active at a time.
- Plays a soft **C–E–G–C ready arpeggio** after audio is initialized and the first MIDI input opens.
- Cancels the arpeggio when you begin playing and clears held notes when a controller disconnects.
- Supports velocity, sustain, pitch bend, channel pressure, and MIDI control changes.
- Works offline after its packages and SoundFont have been installed.

## Hardware

- Raspberry Pi 4 Model B, adequate power supply, and microSD or USB boot storage.
- Raspberry Pi OS Lite **64-bit / Debian Bookworm**, the physically tested base.
- Alesis Q49 or another ALSA-compatible USB MIDI controller, plus a USB data cable.
- Powered speakers or headphones connected to the Pi's **3.5 mm jack**.
- Internet access for initial package installation. A directly connected Mac must have Internet Sharing enabled; an Ethernet cable alone does not provide internet.

The keyboard sends MIDI. **Audio comes from the Raspberry Pi**, not from the Q49's USB connection. A DIN-only controller needs a separate USB MIDI interface. The Pi must already support USB boot if you choose USB storage; this project does not modify its EEPROM boot order.

## Install on the Raspberry Pi

Install Raspberry Pi OS Lite, boot it, and open a local or SSH terminal. Clone this repository:

```bash
git clone https://github.com/valentinovergara/pianoberry-keys.git
cd pianoberry-keys
sudo bash scripts/install.sh
```

The installer uses Debian packages, creates the unprivileged `ivorybox` service account, installs the app under `/opt/ivorybox`, and enables startup. It preserves an existing `/etc/ivorybox/config`.

For a **fresh Pi 4 jack installation**, the sample configuration uses `plughw:CARD=Headphones,DEV=0`. If your device differs, find its actual name with `aplay -l` and edit `/etc/ivorybox/config` before restarting:

```bash
sudo systemctl restart ivorybox.service
systemctl status ivorybox.service --no-pager
journalctl -u ivorybox.service -b --no-pager
```

After hearing the ready arpeggio, play your keyboard. The arpeggio confirms that the synth opened its audio driver and MIDI input; it cannot verify speaker wiring or volume by itself. Start with speaker volume low.

See [installation and troubleshooting](docs/INSTALL.md) for audio setup, network issues, upgrades, and removal. There is **no prebuilt bootable image** in this release. The scripts in `deploy/usb/` document recovery of an already provisioned device; they are not a replacement for the normal installation above.

## Change voices on the Q49

On the **original Alesis Q49**:

1. Press **MIDI / SELECT**.
2. Press the key labeled **PROGRAM**.
3. Enter a number from **0** to **6** using the numbered keys.
4. Press **ENTER**, then **MIDI / SELECT** again to return to playing.

Enter the number every time, even if it is already shown on the display. These steps follow the [official Q49 quick-start guide](https://www.alesis.com/rscdn/904/documents/q49___quickstart_guide___reva.pdf). Other controllers may display programs as **1–128**: in that case displayed values 1–7 correspond to MIDI values 0–6. The Q49 MKII has different controls; use its own manual.

A voice change releases current notes and sustain, then applies the selected voice to all 16 MIDI channels. Unsupported program numbers and bank changes are ignored. The selection lasts until the service restarts; the configured startup voice is then restored.

## Configuration

Edit `/etc/ivorybox/config`, then restart `ivorybox.service`.

| Setting | Fresh-install default | Meaning |
|---|---|---|
| `AUDIO_DEVICE` | `plughw:CARD=Headphones,DEV=0` | ALSA output device |
| `SOUNDFONT` | `/usr/share/sounds/sf2/FluidR3_GM.sf2` | SoundFont with required bank-0 programs |
| `GAIN` | `0.5` | Synth gain, greater than 0 and at most 2 |
| `PERIOD` | `256` | Requested frames per period; the driver may negotiate another size |
| `MIDI_MATCH` | empty | Optional case-insensitive controller-name filter |
| `SOUND` | `piano` | Startup voice: `piano`, `byte`, `nebula`, `crystal-harp`, `pixel-quest`, `abyss`, or `lofi` |
| `READY_SOUND` | `1` | Set `0` to disable the ready arpeggio |

For example, add `SOUND=abyss` to start with the aquatic pad. The synth runs at 48 kHz with 128-voice polyphony and three requested audio periods. Actual latency depends on the audio driver and hardware; no end-to-end latency guarantee has been measured.

Manual CLI usage is available with `python3 -m ivorybox --help`; an optional package installation exposes `pianoberry-keys` and the compatibility alias `ivorybox`. The systemd installer uses system Python and Debian dependencies rather than pip.

## Development

Python 3.9 or newer is required. The unit tests use fakes and do not need MIDI hardware or audio libraries:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_version.py
bash -n scripts/install.sh
```

GitHub Actions runs the test suite on Python 3.9, 3.11, and 3.13. The real synthesizer has also been exercised on the target Pi to confirm all seven voices generate audio. User testing confirmed piano playback, the Q49, and the ready arpeggio. Subjective sound quality, every controller, and physical latency are not covered by unit tests.

For an optional synthesis check on a Pi with dependencies installed, run `python3 scripts/render_check.py`. It renders every voice without opening the audio device and checks for finite, nonzero, nonclipping output. Add `--output-dir /tmp/pianoberry-previews` to save generic arpeggio WAV previews. This is a software rendering check, not a physical speaker or latency test.

Read [architecture](docs/ARCHITECTURE.md), [hardware validation](docs/HARDWARE-TEST.md), [contributing](CONTRIBUTING.md), and [release policy](docs/RELEASING.md).

## License and credits

Project code is licensed under [MIT](LICENSE). FluidSynth, Mido, python-rtmidi, Debian packages, and SoundFonts retain their own licenses. SoundFont samples and OS images are **not** distributed in this repository. Before redistributing an image with FluidR3, read `/usr/share/doc/fluid-soundfont-gm/copyright` on the Pi.

Built on [FluidSynth](https://www.fluidsynth.org/api/index.html), [Mido](https://mido.readthedocs.io/), and [Raspberry Pi OS](https://www.raspberrypi.com/software/). This project is not affiliated with Alesis or Raspberry Pi Ltd.
