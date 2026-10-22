# Architecture

USB MIDI → ALSA / RtMidi → Mido → voice routing → libfluidsynth → ALSA → speakers.

The product is Orphic Keys; `ivorybox` remains the internal Python module and Linux service for compatibility. Python discovers inputs every 500 ms and drains MIDI events with a 1 ms loop wait. FluidSynth renders audio in its native thread; Python does not process audio samples in the performance path.

One controller stays selected until it disappears. A Q49 is preferred when a new selection is made, then the first sorted eligible input. `MIDI_MATCH` restricts selection. Multiple simultaneous controllers are not supported.

The ready cue schedules notes from the MIDI loop without sleeps. It starts only when the first input opens, runs once per process, and cancels before a player's note is dispatched. Channel 16 carries the cue, and all channels use the selected voice.

Program Changes 0/1/2 select piano/BYTE/NEBULA globally. A voice change releases sustain and notes before selecting bank-0 instruments and applying per-voice effects. Bank messages, SysEx, and other program numbers are ignored. MIDI disconnects clear voices and controls; the selected voice and effects remain. The startup voice comes from configuration, rather than persisting every MIDI program change to disk.

MIDI discovery errors retry in-process. Fatal audio errors cause systemd to restart the app. Device disappearance and reappearance entirely between two polling intervals is not guaranteed to be detected. Restart the service if needed.

The core app has no web interface, telemetry, network listener, or cloud account. Logs use journald. The standard installation runs under an unprivileged account and does not enable SSH. Optional recovery/maintenance tooling is separate and documented under `deploy/usb`.
