#!/bin/bash
set -euo pipefail
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
exec >> "$BOOT/IVORYBOX-ACCESO.txt" 2>&1
trap 'echo "ERROR acceso: línea $LINENO"; sync' ERR
echo "Configurando acceso: $(date -Is)"
if ! test -x /usr/sbin/sshd || ! command -v sudo >/dev/null; then
 cp -R "$BOOT/ivorybox-offline/repo" /opt/ivorybox-offline/
 chmod -R a+rX /opt/ivorybox-offline/repo
 echo 'deb [trusted=yes] file:/opt/ivorybox-offline/repo ./' > /opt/ivorybox-offline/local.list
 OPTS=(-o Dir::Etc::sourcelist=/opt/ivorybox-offline/local.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/opt/ivorybox-offline/lists -o Acquire::Languages=none)
 export DEBIAN_FRONTEND=noninteractive
 apt-get "${OPTS[@]}" update
 apt-get "${OPTS[@]}" install -y --no-install-recommends openssh-server sudo
fi
if ! id ivoryadmin >/dev/null 2>&1; then useradd -m -s /bin/bash -p '*' ivoryadmin; fi
install -d -m 700 -o ivoryadmin -g ivoryadmin /home/ivoryadmin/.ssh
install -m 600 -o ivoryadmin -g ivoryadmin /opt/ivorybox-access/authorized_key.pub /home/ivoryadmin/.ssh/authorized_keys
printf 'ivoryadmin ALL=(root) NOPASSWD: /usr/bin/systemctl restart ivorybox.service, /usr/bin/systemctl stop ivorybox.service, /usr/bin/systemctl start ivorybox.service, /usr/bin/journalctl -u ivorybox.service --no-pager -n 100\n' > /etc/sudoers.d/ivorybox-maintenance
chmod 440 /etc/sudoers.d/ivorybox-maintenance
visudo -cf /etc/sudoers.d/ivorybox-maintenance
ssh-keygen -A
# Maintenance can edit only piano code and its configuration.
chown -R ivoryadmin:ivoryadmin /opt/ivorybox/ivorybox
chown ivoryadmin:ivoryadmin /etc/ivorybox/config
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/00-ivorybox.conf <<'CONFIG'
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
AllowUsers ivoryadmin
CONFIG
mkdir -p /run/sshd
/usr/sbin/sshd -t
systemctl enable ssh
systemctl restart ssh
hostnamectl set-hostname ivorybox
if command -v nmcli >/dev/null; then
 if ! nmcli -t -f NAME connection show | grep -qx ivorybox-wired; then
  nmcli connection add type ethernet ifname eth0 con-name ivorybox-wired ipv4.method auto ipv6.method auto connection.autoconnect yes connection.autoconnect-priority 100
 fi
 nmcli --wait 20 connection up ivorybox-wired || true
fi
systemctl disable ivorybox-access.service
ip -brief address
systemctl status ssh --no-pager
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
printf '\nSSH_LISTO — usuario ivoryadmin, solo clave del Mac.\n'
sync
