# Hardware validation

## Observed on the original device

Raspberry Pi 4 Model B, Raspberry Pi OS Lite arm64 / Debian 12 Bookworm, onboard `Headphones` ALSA output, Alesis Q49 USB MIDI, and FluidR3 GM SoundFont.

- User confirmed audible piano playback and the ready arpeggio.
- ALSA enumerated the Q49 MIDI input; service logs confirmed it opened successfully.
- Native FluidSynth rendering on the target Pi produced nonzero audio for piano, BYTE, NEBULA, CRYSTAL HARP, PIXEL QUEST, ABYSS, and DUSTY KEYS.
- The service remained active after voice updates.

This does not certify all USB controllers or prove a measured latency. BYTE/NEBULA subjective evaluation and long-session stress testing remain separate checks.

## Test protocol for a release

Record OS image, board revision, power supply, exact controller model, audio device, SoundFont, FluidSynth version, and configuration.

- Cold boot with Q49: hear the ready cue and play without launching an app.
- Boot without a controller: connect later and confirm the cue plays then.
- Disconnect with a held note and sustain: confirm silence; reconnect and play.
- Check velocity, chords, sustain, channels 1 and 10, and pitch bend.
- Select programs 0–6; confirm distinct voices and no held notes across changes.
- Start playing during the ready cue: player input must take priority.
- Play at least 30 minutes and inspect logs, temperature, and audio dropouts.
- Reboot with `SOUND=nebula`, then with `READY_SOUND=0`.
- Test a second controller and record the actual model/result.
- Confirm operation offline after installation.
- Measure physical note-to-audio latency externally if available; do not infer it from the requested buffer size alone.

For layered modes, verify sustain and pitch bend affect both layers, and switching to piano leaves no held layer or filter residue. PIXEL QUEST is intentionally monophonic per channel.
