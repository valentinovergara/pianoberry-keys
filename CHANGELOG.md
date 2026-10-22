# Changelog

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
