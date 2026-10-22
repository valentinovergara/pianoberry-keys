# Versioning and releases

The public project is **Orphic Keys**. `ivorybox` remains the module/service name to support devices installed under the original IvoryBox name. The default branch is `main`.

## Semantic versioning

- PATCH: compatible bug fixes.
- MINOR: compatible features and new voices.
- MAJOR: incompatible changes.

The project is currently 0.x and experimental. Document any configuration or behavior break. Prefer concise commits such as `feat:`, `fix:`, and `docs:`. Open pull requests from feature branches and keep each change focused.

## Release checklist

1. Update `ivorybox/__init__.py`, `pyproject.toml`, and `CHANGELOG.md` with the same version.
2. Run the README checks. Repeat physical validation when changing MIDI, audio, or installation.
3. Commit the final state and create an annotated `vX.Y.Z` tag.
4. Push `main` and that tag, then create a GitHub Release with the matching changelog.
5. State what hardware was actually tested and what remains unverified.

CI is read-only and requires no secrets. There is no automatic PyPI publication, OS-image build, or deployment to a Raspberry Pi. Never include SSH keys, device logs, SoundFonts, package caches, or user configuration in a release archive. Historical IvoryBox tags describe earlier versions; retain them as history.
