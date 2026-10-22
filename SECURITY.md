# Security

The core app listens to local MIDI and produces audio. It does not expose a network service. The standard installer needs administrative access to install packages but runs the instrument under an unprivileged account.

Optional SSH provisioning is a separate maintenance feature. Protect its client key, use a trusted local network, and revoke access when no longer needed. Never commit private keys, tokens, device logs, or populated user configuration.

For a vulnerability, use GitHub's private vulnerability reporting feature if enabled, or contact the maintainer through a private channel. Do not include credentials or exploit details in a public issue before coordinating a fix.
