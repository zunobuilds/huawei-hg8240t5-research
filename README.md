<h1 align="center">Huawei HG8240T5</h1>

<p align="center">
  <img src="images/ai-assisted.svg" alt="AI-assisted" width="100" height="22" />
</p>

I am investigating a retired Huawei optical network router (ONR), including its hardware, management interface and possible reuse.

I used a Huawei HG8240T5 running firmware customized for [Singtel](https://www.singtel.com/), an internet service provider (ISP) in Singapore. Findings apply to the tested SINGTEL2 build; other units and firmware may differ.

![Huawei HG8240T5 enclosure viewed from a front corner, showing the vented top and Singtel branding](images/device/hg8240t5-exterior.jpg)

## Findings and vulnerabilities

- **Confirmed vulnerability — [ONR-WEB-001](docs/findings/ONR-WEB-001.md):** I reproduced unauthenticated exposure from four WAN/ONT resources containing configuration and device-state data on the tested management LAN.
- **Exposed information:** three WAN profiles, MAC addresses, VLAN/service configuration, connection mode/status flags and optical network terminal (ONT) state. Internet-side exposure was not established.
- **Unresolved observation:** a password-labelled field contained the same opaque 64-character hexadecimal value across profiles. I have not established its meaning or usability, or recovered a password from it.
- **Hardware findings:** I documented the PCB and component identification in the [hardware guide](docs/hardware.md), with photographs and evidence limits.
- **Access results:** I have not obtained shell access, arbitrary command execution, a firmware dump or a verified UART pinout.

## Start here

- [Device and firmware](docs/device.md)
- [Hardware and photographs](docs/hardware.md)
- [Finding summary and limits](docs/findings/ONR-WEB-001.md)
- [Offline tools: first example](tools/README.md#first-offline-example)
- [All documentation](docs/README.md)

## Safety and ownership

I used AI assistance for code, analysis and documentation, so this research may contain errors. Experimental hardware work can cause injury, damage, data loss or service disruption. Equipment testing requires authorization; the [full disclaimer](DISCLAIMER.md) describes the limitations.

Original contributions use the [MIT License](LICENSE), with **ABSOLUTELY NO WARRANTY**, to the extent permitted by applicable law. Device hardware and original firmware are third-party works outside the repository license. See [ownership and license scope](NOTICE.md).
