# Contributing

Thanks for helping make PianoBerry Keys a better standalone instrument.

For a bug report, include the app version, Pi model, OS, controller model, audio device, steps to reproduce, and a short relevant log excerpt. Remove personal data and credentials before sharing logs.

Run the checks in the README before opening a pull request. Keep the audio path in FluidSynth, avoid blocking MIDI processing, and preserve the unprivileged service model. Any new SoundFont or sample asset needs an explicit compatible redistribution license; link to it rather than committing samples by default.

Hardware-dependent changes should include the exact setup and observed result. Mock-based tests cannot replace an audible hardware check. Preserve the `ivorybox` module, service, and configuration paths unless the change includes a documented migration.
