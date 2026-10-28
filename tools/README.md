# Offline tools

Run commands from the repository root. Tools read saved files; neither sends device requests nor executes supplied JavaScript or model output.

| Tool | Requirements | First useful result |
| --- | --- | --- |
| [JavaScript inventory](js-inventory/README.md) | Node.js 22.x (22.18+) or 24.11+, npm | JSON shapes from a synthetic script |
| [Local file review](local-review/README.md) | Linux, Rust/Cargo 1.99+ | Saved task identity without inference |

Dependency installation requires access to package registries and local disk writes. Use reviewed inputs: outputs may reveal field names, prompts or evidence. Generated files, caches and results are excluded from Git. The [optional model setup](../docs/local-models.md) is separate from offline checks.
