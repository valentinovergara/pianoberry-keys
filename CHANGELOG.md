# Changelog

## [0.4.0] - 2026-10-22

- Added CRYSTAL HARP (program 3), PIXEL QUEST (4), ABYSS (5), and DUSTY KEYS (6).
- Added quiet layered harp/crystal textures using internal MIDI channels 17–32.
- Added per-voice filter, attack, release, attenuation, and tuning offsets. Offsets reset when changing modes.
- PIXEL QUEST uses per-channel monophonic pulse playback; all other voices remain polyphonic.
- Preserved programs 0/1/2 for piano/BYTE/NEBULA and the existing readiness cue.
- Added rendering checks and optional WAV previews; all seven voices rendered on the target Pi without clipping in the test phrase.
- Uses only the installed FluidR3 SoundFont; no extracted game samples or soundtrack recordings.

## [0.3.1] - 2026-10-22

- Renamed the public project and repository to **PianoBerry Keys**.
- Updated English guides, project links, CLI branding, and service description.
- Added the `pianoberry-keys` CLI while retaining `orphic-keys` and `ivorybox` aliases.
- Existing `ivorybox` service, module, configuration paths, and device installations remain compatible.

## [0.3.0] - 2026-10-22

### Added
- Public identity: **Orphic Keys**, inspired by Orpheus.
- English installation, configuration, troubleshooting, contribution, and release documentation.
- Optional `orphic-keys` CLI entry point; the `ivorybox` compatibility alias remains.
- Fresh Pi 4 configuration defaults to the tested onboard audio jack.

### Compatibility
- Existing `ivorybox` Python imports, service name, account, and Linux paths remain unchanged.
- Existing device configuration is preserved by the installer.
- The public documentation release has not been deployed to the original device; its working 0.2.0 installation remains available.

## [0.2.0] - 2026-10-22

- Added BYTE, a sampled square-wave lead inspired by chiptune.
- Added NEBULA, a warm pad with reverb and chorus.
- MIDI Program Changes 0/1/2 select piano/BYTE/NEBULA globally.
- `SOUND` chooses the startup voice; switching clears held notes and sustain.
- All three voices generated audio in native rendering on the target Raspberry Pi.

## [0.1.1] - 2026-10-22

- Added a soft C–E–G–C ready arpeggio after the first MIDI input opens.
- The cue does not block MIDI and cancels when the player starts or disconnects.
- Added `READY_SOUND=0` and `--no-ready-sound` to disable it.
- Fixed a stale server-key reference in optional SSH provisioning.

## [0.1.0] - 2026-10-22

- Initial experimental IvoryBox release: FluidSynth piano, Q49 preference, MIDI reconnection, sustain, velocity, pitch bend, systemd startup, and CI.
- Initial release preceded physical hardware validation; later testing confirmed the original device works.
