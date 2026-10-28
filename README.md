<h1 align="center">Huawei HG8240T5</h1>

<p align="center">
  <img src="images/ai-assisted.svg" alt="AI-assisted" width="100" height="22" />
</p>

Independent research into a retired optical network router (ONR), for readers interested in embedded hardware, security analysis and offline research tools.

This project studies a Huawei HG8240T5 running firmware customized for [Singtel](https://www.singtel.com/), an internet service provider (ISP) in Singapore. Findings apply to the tested SINGTEL2 build; other units and firmware may differ.

![Huawei HG8240T5 enclosure viewed from a front corner, showing the vented top and Singtel branding](images/device/hg8240t5-exterior.jpg)

## Findings and vulnerabilities

- **Confirmed vulnerability — [ONR-WEB-001](docs/findings/ONR-WEB-001.md):** four WAN/ONT resources exposed configuration and device-state data without authentication on the tested management LAN.
- **Exposed information:** three WAN profiles, MAC addresses, VLAN/service configuration, connection mode/status flags and optical network terminal (ONT) state. Internet-side exposure was not established.
- **Unresolved observation:** a password-labelled field contained the same opaque 64-character hexadecimal value across profiles. Its meaning and usability are unknown; password recovery was not demonstrated.
- **Hardware findings:** PCB and component identification are documented in the [hardware guide](docs/hardware.md), with photographs and evidence limits.
- **Access results:** no shell access, arbitrary command execution, firmware dump or verified UART pinout has been established.

## Start here

- [Device and firmware](docs/device.md)
- [Hardware and photographs](docs/hardware.md)
- [Finding summary and limits](docs/findings/ONR-WEB-001.md)
- [Offline tools: first example](tools/README.md#first-offline-example)
- [All documentation](docs/README.md)

## Safety and ownership

This independent, **AI-assisted** research may contain errors. **Do not try this at home:** experimental hardware work can cause injury, damage, data loss or service disruption. Obtain authorization before testing equipment; read the [full disclaimer](DISCLAIMER.md).

Original contributions use the [MIT License](LICENSE), with **ABSOLUTELY NO WARRANTY**, to the extent permitted by applicable law. The author did not design the device hardware or firmware; the license does not cover them. See [ownership and license scope](NOTICE.md).
