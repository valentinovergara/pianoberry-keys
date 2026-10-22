#!/bin/bash
set -euo pipefail
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
install -d -m 700 /opt/ivorybox-access
cp "$BOOT/ivorybox-access/setup.sh" /opt/ivorybox-access/setup.sh
cp "$BOOT/ivorybox-access/authorized_key.pub" /opt/ivorybox-access/authorized_key.pub
cat > /etc/systemd/system/ivorybox-access.service <<'UNIT'
[Unit]
Description=IvoryBox key-based SSH setup
After=network.target
StartLimitIntervalSec=0
[Service]
Type=oneshot
ExecStart=/bin/bash /opt/ivorybox-access/setup.sh
Restart=on-failure
RestartSec=20
TimeoutStartSec=0
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable ivorybox-access.service
sed -i 's| systemd.run=[^ ]*||g; s| systemd.run_success_action=[^ ]*||g; s| systemd.unit=kernel-command-line.target||g' "$BOOT/cmdline.txt"
sync
