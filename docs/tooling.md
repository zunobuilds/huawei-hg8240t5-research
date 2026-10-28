# Tools and workflow

| Tool | Actual role | Limit |
| --- | --- | --- |
| Codex | Supervised orchestration, code review, analysis and documentation | Can make mistakes; claims require evidence |
| Playwright | Controlled WebUI interaction and independent browser comparisons | No live collectors are included here |
| Ollama | Local model serving | No model runtime or weights bundled |
| Qwen3 32B | Selected local evidence review | No autonomous execution; historical tasks are not all attributed to it |
| REA | Constrained read-only analysis of saved material | Partial graphs and semantic unknowns are not vulnerabilities |
| Rust client | Deduplicated file tasks and streamed local-review results | Responses are text for review, never automatically executed |
| Photo mosaic | Native-source alignment, local focus selection and tiled lossless rendering | Planar geometry, source blur and tall-component parallax limit results |
| Static JavaScript inventory | Syntax-tree extraction of declarations and field shapes | Does not execute scripts or establish backend behavior |

The public Rust client is adapted for this repository's paths and Qwen3-only configuration. The JavaScript utility adapts the private inventory's static parsing approach for arbitrary local files and suppresses literal values by default. Neither utility contacts the device.

See [offline tool instructions](../tools/README.md) and [local model setup](local-models.md). Keep generated outputs private: an inventory's variable names and shape metadata may still disclose details. The tools do not replace a secret scanner or an authorization boundary.

The [photo mosaic guide](../tools/photo-mosaic/README.md) documents safe intake, resumable registration and focus selection. Numerical and image-processing libraries are required separately; photographs, generated outputs and installed dependencies are excluded.
