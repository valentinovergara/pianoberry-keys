#!/bin/bash
set -euo pipefail
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
exec >> "$BOOT/IVORYBOX-ACTUALIZACION.txt" 2>&1
echo "Actualizando IvoryBox y reparando SSH: $(date -Is)"
# Discard only the stale custom HostKey directive; keep key-only access settings.
if [ -f /etc/ssh/sshd_config.d/00-ivorybox.conf ]; then
 sed -i '\|^HostKey /etc/ssh/ssh_host_ivorybox_ed25519_key$|d' /etc/ssh/sshd_config.d/00-ivorybox.conf
fi
install -m 644 "$BOOT/ivorybox-update/ssh-setup.sh" /opt/ivorybox-access/setup.sh
# Replace app files while the live MIDI service has not started yet.
for name in __init__.py __main__.py app.py engine.py cue.py; do
 install -m 644 "$BOOT/ivorybox-update/$name" "/opt/ivorybox/ivorybox/$name"
done
if id ivoryadmin >/dev/null 2>&1; then chown -R ivoryadmin:ivoryadmin /opt/ivorybox/ivorybox; fi
/usr/bin/python3 -m py_compile /opt/ivorybox/ivorybox/app.py /opt/ivorybox/ivorybox/cue.py
systemctl enable ivorybox-access.service
systemctl enable ivorybox.service
sed -i 's| systemd.run=[^ ]*||g; s| systemd.run_success_action=[^ ]*||g; s| systemd.unit=kernel-command-line.target||g' "$BOOT/cmdline.txt"
echo 'Actualizacion 0.1.1 preparada. SSH se configurara en el siguiente arranque.'
sync
