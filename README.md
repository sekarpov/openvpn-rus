# OpenVPN RUS

Production-oriented automation for OpenVPN server provisioning and client profile lifecycle management using `Makefile` and Ansible.

## What this project does

- Provisions OpenVPN on a clean Ubuntu/Debian host.
- Initializes and maintains Easy-RSA PKI on the server.
- Creates inline client `.ovpn` profiles locally in `clients/<profile>/`.
- Revokes and renews client certificates without manual PKI operations.
- Renews the server certificate without touching existing client profiles.
- Keeps server provisioning and day-2 client operations separated.

## Security notes

- Client `.ovpn` files contain private keys. They must not be committed to git.
- This repository now ignores `clients/**/*.ovpn`, but already tracked files remain tracked until removed from git history/index manually.
- The CA private key is kept on the VPN server for operational simplicity. That is acceptable for a small-team setup, but not equivalent to an offline CA.

## Project layout

```text
Makefile
README.md
clients/
provisioning/
scripts/
```

`provisioning/` contains the full Ansible implementation. `clients/` stores generated local client artifacts.

## Prerequisites

- Control machine with `ansible-playbook` available.
- SSH access to the target server.
- Ubuntu/Debian-based target host.

## Initial setup

1. Create inventory files:

```bash
cp provisioning/inventories/production/hosts.yml.dist provisioning/inventories/production/hosts.yml
cp provisioning/inventories/production/group_vars/all.yml.dist provisioning/inventories/production/group_vars/all.yml
cp provisioning/inventories/production/group_vars/all.vault.yml.dist provisioning/inventories/production/group_vars/all.vault.yml
```

2. Edit inventory and group vars:

- `provisioning/inventories/production/hosts.yml`
- `provisioning/inventories/production/group_vars/all.yml`

At minimum set:

- `ansible_host`
- `ansible_user`
- `openvpn_remote_host`
- `openvpn_public_interface`

If the target host is an end-of-life Debian release such as `buster`, either upgrade the OS first or explicitly allow archived mirrors:

```yaml
openvpn_manage_debian_eol_repos: true
```

That rewrites Debian mirror URLs to `archive.debian.org` during provisioning. Treat it as a temporary compatibility path, not a long-term production baseline.

## Commands

Provision a clean server:

```bash
make provision INVENTORY=production
```

Create a client and fetch the ready-to-use profile locally:

```bash
make client-create INVENTORY=production CLIENT=alice
```

Rebuild an existing client profile from current PKI state:

```bash
make client-config INVENTORY=production CLIENT=alice
```

Renew a client certificate under the same client identity:

```bash
make client-renew INVENTORY=production CLIENT=alice
```

Revoke a client:

```bash
make client-revoke INVENTORY=production CLIENT=alice
```

List client identities:

```bash
make list-clients INVENTORY=production
```

Renew the server certificate:

```bash
make server-renew INVENTORY=production
```

Check service and PKI status:

```bash
make status INVENTORY=production
```

## Renewal model

### Client renewal

`make client-renew CLIENT=name` performs controlled reissue:

1. Validates the client identity.
2. Revokes the current certificate for that CN.
3. Regenerates `crl.pem`.
4. Reissues a new client certificate and key with the same CN.
5. Rebuilds `clients/<profile>/<name>.ovpn` locally.

This keeps the client identity stable while replacing the certificate material and updating the local artifact automatically.

### Server renewal

`make server-renew` revokes and reissues the server certificate with the same CN, deploys the new files, and restarts the OpenVPN service. Client profiles stay valid because the CA and `tls-crypt` key are preserved.

## Smoke tests

After `make provision`:

- `make status` reports the service as active.
- `make client-create CLIENT=smoke` produces `clients/<profile>/smoke.ovpn`.
- A client can connect using the generated profile.
- `make client-revoke CLIENT=smoke` makes that profile unusable.
- `make client-renew CLIENT=alice` overwrites the same local file path with new certificate material.

## Defaults worth reviewing

- `openvpn_public_interface`
- `openvpn_remote_host`
- `openvpn_push_dns`
- `openvpn_server_cidr`
- `openvpn_client_expire_days`
- `openvpn_server_expire_days`
- `openvpn_ca_expire_days`
- `openvpn_data_ciphers`

## Notes on firewall ownership

This role manages `/etc/iptables/rules.v4` when `openvpn_manage_iptables` is enabled. On a dedicated VPN host that is appropriate. If the server already has a more complex firewall policy, either disable that flag and manage firewall rules elsewhere or adapt the template before provisioning.
