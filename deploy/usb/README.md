# Advanced USB recovery tools

These scripts recover an **already provisioned** IvoryBox/Orphic Keys device. They do not build a ready-to-flash OS image and are not the normal installation entry point. Use the root README for a new installation.

They assume Raspberry Pi OS Bookworm arm64, `/boot/firmware`, and the app source previously placed in `/opt/ivorybox-source/ivorybox`. Review scripts before running them as root. Boot-time hooks change the existing device; preserve its root PARTUUID and keep `cmdline.txt` on one line.

## Offline package recovery

`build_offline.py` reads official package indexes from `offline/` beside the script:

- `bookworm.xz`: `https://deb.debian.org/debian/dists/bookworm/main/binary-arm64/Packages.xz`
- `updates.xz`: `https://deb.debian.org/debian/dists/bookworm-updates/main/binary-arm64/Packages.xz`
- `security.xz`: `https://deb.debian.org/debian-security/dists/bookworm-security/main/binary-arm64/Packages.xz`

It resolves package dependencies, downloads official packages over HTTPS, checks their SHA-256 values against the indexes, and builds `offline/repo/` with a `Packages` index and a manifest. These artifacts and their package licenses are not part of Git. Dependency selection is intentionally small and is not a general Debian dependency solver; validate changes on the target OS.

Place `repo/`, the generated manifest, and `install.sh` under `bootfs/ivorybox-offline/`. Place `offline-bootstrap.sh` in `bootfs/ivorybox-offline-bootstrap.sh`. Append the following to the existing kernel command line once:

```text
systemd.run=/boot/firmware/ivorybox-offline-bootstrap.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target
```

The bootstrap copies the repository to Linux, disables the previous network setup, and enables a local-only APT installation service. Global APT sources are unchanged. The log is `bootfs/IVORYBOX-INSTALACION-OFFLINE.txt`; success creates `/opt/ivorybox-offline/complete`. Failures retry and remain in the log. An audible confirmation is attempted before starting the MIDI service.

## Optional SSH maintenance

This is separate from the standard installer. It creates a key-only `ivoryadmin` account. The client private key stays on the owner's computer; copy only its public key to the Pi. The server generates its own host keys. Verify the initial host fingerprint using a trusted channel; subsequent connections must reject identity changes.

The account may edit `/opt/ivorybox/ivorybox` and `/etc/ivorybox/config`. Its sudo rule permits only exact start/stop/restart commands for `ivorybox.service` and reading its last 100 journal entries. It does not grant unrestricted sudo or permission to edit systemd units.

Place `ssh-setup.sh` as `bootfs/ivorybox-access/setup.sh` and the client's public key as `authorized_key.pub` in that folder. Place `ssh-bootstrap.sh` as `bootfs/ivorybox-ssh-bootstrap.sh`, then use the same one-time kernel parameters with that script's path. SSH/sudo packages must already be installed or available in the local repository. The setup log is `IVORYBOX-ACCESO.txt`.

A directly connected Mac must share its internet connection to the correct Ethernet adapter; the Pi requests DHCP on `eth0`. No router port forwarding or internet-facing access is configured. Revoke maintenance access by removing the user's authorized key and `/etc/sudoers.d/ivorybox-maintenance`, and disable SSH if unused.

## Existing-device update hook

`repair-and-update.sh` is a historical recovery hook for the 0.1.1 update and stale SSH HostKey configuration. It expects its update files in `bootfs/ivorybox-update/`. It is not a generic updater for later releases. Prefer the standard installer or a reviewed SSH deployment for current versions.
