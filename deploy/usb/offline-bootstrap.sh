#!/bin/bash
set -euo pipefail
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
install -d /opt/ivorybox-offline
cp -R "$BOOT/ivorybox-offline/repo" /opt/ivorybox-offline/
chmod -R a+rX /opt/ivorybox-offline
cp "$BOOT/ivorybox-offline/install.sh" /opt/ivorybox-offline/install.sh
systemctl disable ivorybox-setup.service || true
systemctl disable ivorybox-diagnostic.service || true
cat > /etc/systemd/system/ivorybox-offline.service <<'UNIT'
[Unit]
Description=IvoryBox offline installation
After=local-fs.target sound.target
ConditionPathExists=!/opt/ivorybox-offline/complete
StartLimitIntervalSec=0
[Service]
Type=oneshot
ExecStart=/bin/bash /opt/ivorybox-offline/install.sh
Restart=on-failure
RestartSec=30
TimeoutStartSec=0
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable ivorybox-offline.service
sed -i 's| systemd.run=[^ ]*||g; s| systemd.run_success_action=[^ ]*||g; s| systemd.unit=kernel-command-line.target||g' "$BOOT/cmdline.txt"
sync
