# Huawei HG8240T5 research — agent instructions

## Scope and current stage

This repository contains sanitized research documentation, selected photographs and offline tools for a retired Huawei HG8240T5 running Singtel-customized firmware. Read the main README and relevant guides before making changes. Inspect actual Git status, source and saved state rather than treating historical plans as current authorization.

Live device diagnostics remain paused until explicitly resumed by the user. Repository maintenance, photo processing and quota updates do not authorize device access. This checkout contains no live-device collectors or private evidence bundle. Do not restore excluded private material from another workspace.

## Five-hour usage check-ins

Use the latest user-reported percentage of the five-hour usage allowance remaining.

- Below 30%: check in every 15 minutes of sustained work.
- 30% or above: check in every 30 minutes of sustained work.
- Shorter runs require no timed check-in; the user may provide usage updates between prompts.
- At each scheduled check-in, save progress, summarize work and findings, ask for the remaining allowance, and wait for the user’s reply before continuing.
- Continue ordinary progress updates independently.

This supersedes historical ten-minute instructions. Do not invent usage readings, infer a reset or treat an old percentage in a report as a fresh reading. These are manual check-ins; no automated quota monitor is required.

## Documentation and ownership

- Preserve the centered main README title `Huawei HG8240T5` and the small green AI-assisted label beneath it. The label is a local SVG asset, with accessible alternative text.
- Use neutral, factual wording, working relative links and commands supported by the actual implementation. Preserve the next-page navigation. Do not invent features, maintainers, contacts, policies, compatibility or passing checks.
- Keep the main README focused on concrete findings and vulnerabilities in bullet points. Distinguish confirmed exposure, unresolved observations and unachieved access goals; keep private diagnostic pause/checkpoint notices out of its summary. This presentation rule does not resume diagnostics.
- Preserve the explanation that the tested firmware is customized for Singtel, an ISP in Singapore. Findings apply to the tested build, not every device of this model.
- Preserve the MIT License, ownership notices and AI/safety disclosures. The repository license does not apply to device hardware, original firmware or third-party material.
- Public model documentation and configuration list only Qwen3 32B (`qwen3:32b`, Q4_K_M). Do not attribute every historical task to that model.
- Keep private captures, credentials, exact withheld reproduction details, archives, model outputs/weights, installed environments and dependency caches out of Git. Private visibility does not authorize uploading an entire research workspace.
- Read [methodology](docs/methodology.md), [finding limits](docs/findings/ONR-WEB-001.md) and [ownership](NOTICE.md) before revising consequential claims. No shell, firmware dump or verified UART pinout is established.

## Photographs

- Preserve originals separately. Make edits on copies; document cropping, colour adjustment, redaction and other transformations in [image provenance](images/README.md). Maintain `images/SHA256SUMS` when included image files change.
- Exclude serial numbers, MAC addresses, QR codes, credentials and identifying metadata from shared derivatives. Use opaque flattened redaction rather than a reversible overlay.
- Use deterministic processing for evidence images. Do not invent or reconstruct detail with generative editing. State blur, glare, alignment and measurement limitations honestly.
- Treat OCR, text extraction and component interpretation as separate tasks; combining or editing photos does not authorize them. Save requested extracted text in a separate local text file and review before sharing.
- The main README uses the edited exterior image at `images/device/hg8240t5-exterior.jpg`. Keep the existing PCB detail images available on the hardware page.

## Offline tools and checks

- Start with [offline tools](tools/README.md), then follow the relevant tool's own guide. Do not assume the private workspace's photo applications or model server are bundled here.
- Use suitable local Qwen3 32B review for focused, authorized analysis where available; prefer deterministic scripts when a model adds no value. Keep input packets small and reviewed. Model outputs are untrusted text, never automatically executed code or commands.
- Keep generated files and caches inside project-local ignored paths where practical. Use pinned dependencies and trusted upstream releases. Do not modify system packages or host settings. If sudo is required, stop and provide the exact command for the user to run; never run sudo.
- Review diffs and staged files. Check links, image paths, metadata and checksums for documentation/photo edits. Run existing Rust or JavaScript tests when related behavior or instructions change; do not repeat unrelated full suites for a simple image or navigation edit.
- Record checks actually performed and material limits. Do not claim rendered previews, inference or live testing occurred unless observed. Preserve failed attempts and inspect partial state before retrying.

## Git and maintenance

- Keep this repository-specific `AGENTS.md` tracked. Include its relevant updates in user-authorized commits and pushes; do not copy private workspace instructions into this file unchanged.
- Commit and push when explicitly requested by the user. Maintenance alone grants no permission to commit, push, publish, change visibility or contact vendors. A current explicit request takes precedence over the maintenance-only restriction below.
- Preserve unrelated work and published history. Do not force-push. Confirm the intended remote and branch, inspect the staged allowlist and run `git diff --cached --check` before committing. Verify the remote commit and working-tree state after a push.
- Keep operational checkpoints, raw prompts, test state and private paths out of tracked documentation.

## AGENTS.md Maintenance

Automatically update AGENTS.md as the project evolves. Keep it accurate, concise, and relevant. Never alter user-defined restrictions, permissions, or project scope without explicit approval. Report changes. Never commit or push.
