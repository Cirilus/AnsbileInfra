sni_finder
==========

Finds SNI candidates for a server IP with `hawshemi/SNI-Finder` and prints the
best candidate discovered for that host.

How it works
------------

- The role runs on the Ansible control machine, not on the VPS.
- It downloads the official `sni-finder` release binary using the upstream
  `sni-finder-run.sh` helper script.
- It scans around the server IP and collects candidate domains in `domains.txt`.
- It ranks discovered candidates by TLS handshake latency and prints the fastest
  reachable domain as the best SNI candidate.

Defaults
--------

- `sni_finder_target_ip`: uses `ansible_host` first and falls back to
  `ansible_default_ipv4.address`.
- `sni_finder_threads`: `128`
- `sni_finder_timeout`: `4`
- `sni_finder_top_count`: `10`

Usage
-----

Include the role and run it explicitly:

```bash
ansible-playbook init_server.yml --tags sni_finder
```

You can override the IP manually when needed:

```yaml
- role: sni_finder
  sni_finder_target_ip: "203.0.113.10"
```
