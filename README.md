# Huawei HG8240T5 research

Independent research into a retired optical network router (ONR), for readers interested in embedded hardware, security analysis and offline research tools.

This project studies a Huawei HG8240T5 running firmware customized for [Singtel](https://www.singtel.com/), an internet service provider (ISP) in Singapore. Findings apply to the tested SINGTEL2 build; other units and firmware may differ.

![Huawei HG8240T5 enclosure viewed from a front corner, showing the vented top and Singtel branding](images/device/hg8240t5-exterior.jpg)

## Research status

Device diagnostics are paused. A LAN information disclosure was independently reproduced. Shell access, firmware extraction and a UART pinout have not been established. Exact reproduction details and raw evidence remain private.

## Start here

- [Device and firmware](docs/device.md)
- [Hardware and photographs](docs/hardware.md)
- [Finding summary and limits](docs/findings/ONR-WEB-001.md)
- [Offline tools: first example](tools/README.md#first-offline-example)
- [All documentation](docs/README.md)

## Safety and ownership

This independent, **AI-assisted** research may contain errors. **Do not try this at home:** experimental hardware work can cause injury, damage, data loss or service disruption. Obtain authorization before testing equipment; read the [full disclaimer](DISCLAIMER.md).

Original contributions use the [MIT License](LICENSE), with **ABSOLUTELY NO WARRANTY**, to the extent permitted by applicable law. The author did not design the device hardware or firmware; the license does not cover them. See [ownership and license scope](NOTICE.md).
