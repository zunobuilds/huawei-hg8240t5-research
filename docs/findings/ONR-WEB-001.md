# ONR-WEB-001: unauthenticated WAN/ONT information disclosure

**Status:** confirmed read-only exposure on the tested management LAN. Severity has not been scored. This is an internal finding identifier, not an assigned CVE.

Tested device: HG8240T5, hardware 17ED.A, firmware V5R021C10S235 / SINGTEL2. Diagnostics are paused; this summary was prepared from saved evidence.

## Verified observations

Four exact resources returned populated WAN or optical network terminal (ONT) data after normal logout. An independent fresh browser process reproduced the behavior without reading credentials, submitting a login or sending Cookie headers. A protected device-information control returned 403. Eight additional exact peer resources also returned 403.

Static parsing identified three WAN profiles with MAC addresses, VLAN/service configuration, mode/status and related flags, plus ONT state. Inspected IP address, gateway and subnet values were unspecified; several DNS and ancillary fields were empty. This does not demonstrate exposure of an active public WAN address.

A password-labelled field held the same opaque 64-character hexadecimal value across profiles and authenticated output. Its algorithm, meaning and usability remain unknown. It is not established as plaintext, a password hash or a usable credential. Anonymous token initializers were empty; no token abuse was demonstrated.

## Limits and correction

Requests were tested in a particular same-origin context on an isolated LAN. Behavior without that context and WAN-side reachability were not independently established. No configuration modification, privilege escalation, arbitrary execution, shell access or firmware disclosure was demonstrated.

An added generic query parameter initially caused misleading 403 responses. Exact observed URLs and request context mattered. HTTP success alone was insufficient: populated data, authentication state and protected controls were checked separately.

Exact endpoints, request sequences, raw responses and opaque values remain private. This public summary is not a runnable reproduction or an independently auditable raw evidence bundle. No vendor contact, external disclosure or matching patched build is claimed.

---

[Next page: Offline tools — first example →](../../tools/README.md#first-offline-example)
