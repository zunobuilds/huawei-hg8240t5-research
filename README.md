# Huawei HG8240T5 research

Independent research into a retired optical network router (ONR), for readers interested in embedded hardware, evidence-based security analysis and offline research tools.

This project studies a Huawei HG8240T5 running firmware customized for [Singtel](https://www.singtel.com/), an internet service provider (ISP) in Singapore. Results describe the tested SINGTEL2 build; they do not establish behavior on other units or firmware.

![PCB backside near connector solder joints, with part of the connector housings visible](images/pcb/pcb-connector-side.jpg)

**Status:** experimental research; device diagnostics are paused. A LAN information disclosure was independently reproduced. Shell access, firmware extraction and a UART pinout have not been established. Exact reproduction details and raw evidence remain private.

## Safety and AI assistance

This is an independent, **AI-assisted research project**. AI-assisted code, analysis and documentation may contain errors.

Original project contributions are provided under the MIT License. Third-party materials remain subject to their respective licenses.

This project comes with **ABSOLUTELY NO WARRANTY**, to the extent permitted by applicable law. See [LICENSE](LICENSE) for the warranty disclaimer and limitation of liability.

**Do not try this at home.** This repository documents experimental research. Attempting similar work can cause injury, device damage, data loss or service disruption. You are responsible for your actions and for obtaining authorization before testing equipment. Read the [full disclaimer](DISCLAIMER.md).

## Explore

- [Hardware and photographs](docs/hardware.md)
- [Finding summary](docs/findings/ONR-WEB-001.md)
- [Documentation index](docs/README.md)
- [Offline tools and examples](tools/README.md)
- [Ownership, attribution and license scope](NOTICE.md)
