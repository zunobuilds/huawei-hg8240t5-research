# Huawei HG8240T5 research — agent instructions

## Scope and current stage

This repository contains sanitized research documentation, selected photographs and offline tools for a retired Huawei HG8240T5 running Singtel-customized firmware. Read the main README and relevant guides before making changes. Inspect actual Git status, source and saved state rather than treating historical plans as current authorization.

Live device diagnostics remain paused until explicitly resumed by the user. Repository maintenance, photo processing and quota updates do not authorize device access. This checkout contains no live-device collectors or private evidence bundle. Do not restore excluded private material from another workspace.

## Five-hour usage check-ins

At each usage checkpoint, run `codex-status` using the shell. Use its five-hour remaining percentage to determine the check-in interval. Never guess.

- Below 18%: check in every 5 minutes of sustained work.
- 18% or above: check in every 10 minutes of sustained work.
- Save progress and summarize work and findings at each checkpoint. If `codex-status` returns a valid five-hour remaining percentage, continue without asking the user or waiting for a reply.
- If the command fails or does not provide a usable five-hour remaining percentage, ask the user for the current usage and wait for the reply before continuing. Do not infer usage or a reset from elapsed time, stale reports or another allowance.
- Below 10% remaining, slow down: stop starting new batches, save state and wrap up. Below 5%, stop new work and leave a complete checkpoint. Never guess usage; use `codex-status` or the user fallback.
- Shorter runs require no timed check-in. Continue ordinary progress updates independently.

This replaces the earlier manual usage questions and all previous checkpoint intervals. No persistent scheduler or background monitoring service is required; run the command at checkpoints during active work.

## Documentation and ownership

- Preserve the centered main README title `Huawei HG8240T5` and the small green AI-assisted label beneath it. The label is a local SVG asset, with accessible alternative text.
- Use neutral, factual wording, working relative links and commands supported by the actual implementation. Preserve the next-page navigation. Do not invent features, maintainers, contacts, policies, compatibility or passing checks.
- Write research narrative in first-person singular as the project author: "I used", "I tested" and "I found". This supersedes the previous ban on first-person writing. Keep the tone factual and professional; avoid detached phrases such as "the documented local model" and "owner-provided". Use direct technical language for instructions, reference tables and code comments where first person adds nothing. Preserve AI attribution, evidence limits, standard license text and all user-defined restrictions. Do not imply unaided manual work or successful tests that the evidence does not establish.
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
- The component-side composite is included on the hardware page as `images/pcb/pcb-component-side.jpg`; lossless masters and original photographs remain local.
- The main README uses the edited exterior image at `images/device/hg8240t5-exterior.jpg`. Keep the existing PCB detail images available on the hardware page.

## Offline tools and checks

- The reusable Python mosaic workflow is in `tools/photo-mosaic/`. Follow its guide for dependencies, archive intake, registration, optional inspected green-PCB masks, projective refinement, focus rendering and reviewed regional composition. Raised components may require a coherent single-source view instead of a fragmented stack. Preserve source white balance; do not apply unverified per-channel colour normalization. Synthetic tests belong in source control; inputs, images, generated reports, feature/render caches and dependency payloads do not. A small residual or a passing synthetic test does not guarantee a fully sharp real PCB image.
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
