# ONR-WEB-001: unauthenticated WAN/ONT information disclosure

**Status:** confirmed read-only exposure on the tested management LAN. I have not assigned a severity score. This is an internal finding identifier, not an assigned CVE.

Tested device: HG8240T5, hardware 17ED.A, firmware V5R021C10S235 / SINGTEL2. I prepared this summary from saved evidence.

## Verified observations

I found four resources returning populated WAN or optical network terminal (ONT) data after normal logout. I used a separate fresh browser process to reproduce the behavior without reading credentials, submitting a login or sending Cookie headers. A protected device-information control returned 403. Eight additional exact peer resources also returned 403.

I used static parsing to identify three WAN profiles with MAC addresses, VLAN/service configuration, mode/status and related flags, plus ONT state. Inspected IP address, gateway and subnet values were unspecified; several DNS and ancillary fields were empty. This does not demonstrate exposure of an active public WAN address.

A password-labelled field held the same opaque 64-character hexadecimal value across profiles and authenticated output. Its algorithm, meaning and usability remain unknown. It is not established as plaintext, a password hash or a usable credential. Anonymous token initializers were empty; no token abuse was demonstrated.

## Limits and correction

Requests were tested in a particular same-origin context on an isolated LAN. I did not independently establish behavior without that context or reachability from the WAN side. I did not demonstrate configuration modification, privilege escalation, arbitrary execution, shell access or firmware disclosure.

An added generic query parameter initially caused misleading 403 responses. Exact observed URLs and request context mattered. HTTP success alone was insufficient: populated data, authentication state and protected controls were checked separately.

I have kept exact endpoints, request sequences, raw responses and opaque values private. This public summary is not a runnable reproduction or an independently auditable raw evidence bundle. No vendor contact, external disclosure or matching patched build is claimed.

---

[Next page: Offline tools — first example →](../../tools/README.md#first-offline-example)
