"""Headless USB MIDI piano with deterministic single-controller selection."""
import argparse
import logging
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from . import __version__
from .engine import Synth
from .cue import ReadyCue
from .presets import PRESETS, PROGRAM_PRESETS

LOG = logging.getLogger("ivorybox")

def configure_headphone_volume(percent, device):
    """Set the Pi 4 jack mixer as the audio-group service user, never as root."""
    if percent is None:
        return
    if not 0 <= percent <= 100:
        raise ValueError("--headphone-volume must be between 0 and 100")
    if "CARD=Headphones" not in device:
        raise ValueError("--headphone-volume requires the onboard CARD=Headphones output")
    result = subprocess.run(
        ["amixer", "-c", "Headphones", "sset", "PCM", str(percent) + "%"],
        check=True, capture_output=True, text=True, timeout=5,
    )
    LOG.info("Headphone mixer: %s", result.stdout.strip())

def choose_port(names, match=""):
    candidates = sorted(n for n in names if "midi through" not in n.lower())
    if match:
        return next((n for n in candidates if match.lower() in n.lower()), None)
    return next((n for n in candidates if "q49" in n.lower()), candidates[0] if candidates else None)

def dispatch(synth, msg):
    channel = getattr(msg, "channel", 0)
    if msg.type == "note_on":
        if msg.velocity:
            synth.send("noteon", channel, msg.note, msg.velocity)
        else:
            synth.send("noteoff", channel, msg.note)
    elif msg.type == "note_off":
        synth.send("noteoff", channel, msg.note)
    elif msg.type == "control_change" and msg.control not in (0, 32):
        synth.send("cc", channel, msg.control, msg.value)
    elif msg.type == "pitchwheel":
        synth.send("pitch_bend", channel, msg.pitch + 8192)
    elif msg.type == "aftertouch":
        synth.send("channel_pressure", channel, msg.value)
    elif msg.type == "program_change" and msg.program in PROGRAM_PRESETS:
        preset = PROGRAM_PRESETS[msg.program]
        synth.select_preset(preset)
        LOG.info("Voice: %s", PRESETS[preset]["name"])
    elif msg.type == "reset":
        synth.panic()
    # Only the three curated program changes are accepted; ignore banks and SysEx.

def run(midi, synth, stop, match="", poll=0.5, ready_sound=True):
    port = None
    active = None
    next_scan = 0.0
    cue = ReadyCue(synth)
    announced = False
    try:
        while not stop.is_set():
            now = time.monotonic()
            if now >= next_scan:
                next_scan = now + poll
                try:
                    names = midi.get_input_names()
                    target = active if active in names else choose_port(names, match)
                    if target != active:
                        if port:
                            port.close()
                            port = None
                        cue.cancel()
                        synth.panic()
                        active = None
                        if target:
                            port = midi.open_input(target)
                            active = target
                            LOG.info("Ready to play: %s", active)
                            if ready_sound and not announced:
                                cue.start(now)
                                announced = True
                        else:
                            LOG.info("Waiting for a USB MIDI controller")
                except (OSError, RuntimeError, EOFError):
                    LOG.exception("MIDI error; retrying")
                    if port:
                        port.close()
                    port, active = None, None
                    cue.cancel()
                    synth.panic()
            if port:
                try:
                    for msg in port.iter_pending():
                        if msg.type == "program_change" or (msg.type == "note_on" and msg.velocity):
                            cue.cancel()
                        dispatch(synth, msg)
                except (OSError, RuntimeError, EOFError):
                    LOG.exception("Controller disconnected; retrying")
                    port.close()
                    port, active = None, None
                    cue.cancel()
                    synth.panic()
            cue.update(time.monotonic())
            stop.wait(0.001)
    finally:
        cue.cancel()
        if port:
            port.close()
        synth.panic()

def main():
    parser = argparse.ArgumentParser(description="PianoBerry Keys: power on, plug in, play")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--soundfont", default="/usr/share/sounds/sf2/FluidR3_GM.sf2")
    parser.add_argument("--device", default="default", help="ALSA output device")
    parser.add_argument("--midi-match", default="", help="Name filter; prefer Q49 if empty")
    parser.add_argument("--gain", type=float, default=0.5)
    parser.add_argument("--period", type=int, choices=(64, 128, 256, 512, 1024), default=128)
    parser.add_argument("--list-midi", action="store_true")
    parser.add_argument("--no-ready-sound", action="store_true",
                        default=os.environ.get("READY_SOUND", "1") == "0",
                        help="Disable the ready arpeggio")
    parser.add_argument("--sound", choices=PRESETS, default=os.environ.get("SOUND", "piano"))
    parser.add_argument("--headphone-volume", type=int, default=os.environ.get("HEADPHONE_VOLUME"),
                        help="Optional Pi 4 jack mixer percentage (0–100)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if not 0 < args.gain <= 2:
        parser.error("--gain must be greater than 0 and at most 2")
    import mido
    mido.set_backend("mido.backends.rtmidi/LINUX_ALSA")
    if args.list_midi:
        print("\n".join(mido.get_input_names()) or "No MIDI controllers")
        return
    if not Path(args.soundfont).is_file():
        parser.error("SoundFont not found: " + args.soundfont)
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    configure_headphone_volume(args.headphone_volume, args.device)
    synth = Synth(args.soundfont, args.device, args.gain, args.period, args.sound)
    try:
        LOG.info("PianoBerry Keys %s — instrument ready", __version__)
        run(mido, synth, stop, args.midi_match, ready_sound=not args.no_ready_sound)
    finally:
        synth.close()

if __name__ == "__main__":
    main()
