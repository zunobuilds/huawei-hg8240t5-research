# Offline tools

I used these offline tools to review saved evidence and process photographs. The examples below run from the repository root. Tools process saved files without device requests or execution of supplied JavaScript or model output. Reading the research requires no tool installation.

| Tool | Requirements | First useful result |
| --- | --- | --- |
| [JavaScript inventory](js-inventory/README.md) | Node.js 22.x (22.18+) or 24.11+, npm | JSON shapes from a synthetic script |
| [Local file review](local-review/README.md) | Linux, Rust/Cargo 1.99+ | Saved task identity without inference |
| [Photo mosaic](photo-mosaic/README.md) | Linux, Python 3.12 and pinned numerical/image libraries | Synthetic registration and focus-selection tests |

## First offline example

With a supported Node.js version and npm installed, run:

```bash
npm ci --ignore-scripts --prefix tools/js-inventory
node tools/js-inventory/inventory.cjs tools/js-inventory/fixtures/sample.js
```

Installation downloads locked dependencies from npm and writes `node_modules` inside the tool directory. The inventory prints JSON describing the fixture's `Profile` function and `profiles` and `token` declarations. It does not execute the fixture's deliberate exception. No device, account, model or model server is needed.

For limits and tests, see the [inventory guide](js-inventory/README.md). For saved text tasks, follow the [Rust offline example](local-review/README.md#offline-example); [model setup](../docs/local-models.md) is optional and separate.

## Validation and generated files

I used automated checks for the offline examples and tests on Linux with Node.js 22.23.1 and Rust/Cargo 1.99.0. Other supported Node.js versions were not exercised here. Rust versions below 1.99 are not claimed as supported.

Reviewed inputs are required because outputs can disclose names, prompts or evidence. Generated files, caches and results are excluded from Git. Sharing outputs requires a separate content review. Installed JavaScript dependencies reside in `tools/js-inventory/node_modules`; removing that directory leaves source files intact. Rust task records reside under `tools/local-review/state`; partial answers require review before record removal.

---

[Go to all documentation →](../docs/README.md)
