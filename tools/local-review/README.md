# Local file review

A Linux Rust client adapted from the private file-review workflow. It saves deduplicated tasks, streams answers and never executes model output. Requires Rust/Cargo 1.99 or later. Run from the repository root; first compilation may download dependencies and runs Cargo dependency build scripts.

## Offline example

```bash
cargo run --locked --manifest-path tools/local-review/Cargo.toml -- submit tools/local-review/examples/prompt.txt tools/local-review/examples/evidence.txt
cargo run --locked --manifest-path tools/local-review/Cargo.toml -- status
```

Expected result: JSON metadata with a 64-character task ID and `queued` status. Files appear under `tools/local-review/state/jobs/`. Identical inputs and settings reuse the same task ID. No server is contacted by `submit` or `status`.

## Optional inference

After completing [local-model setup](../../docs/local-models.md), replace `submit` with `ask` to submit and run the task. A completed task has `completed` status and an `answer.md` beside its saved input and raw stream. These files can contain sensitive data; keep them private.

`run ID` runs one queued task. `recover ID` marks a crashed running job interrupted while holding the inference lock; it does not replay it. Review partial results before submitting a deliberately revised prompt after failure. Output truncation and streams lacking completion fail rather than silently succeeding. Qwen3 32B is the only supported model; `ONR_LOCAL_MODEL`, if set, must be `qwen3:32b`.

Inputs must be UTF-8 text inside this repository. Combined prompt and evidence are limited to 2,048 bytes. Hidden/cache/model/state and credential-like paths are rejected; this filter is not a general secret scanner. Paths must be trusted: checks and task snapshots are not designed to withstand concurrent hostile filesystem changes. The repository root is determined at compile time; rebuild after moving the source tree.

The fixed loopback endpoint is `127.0.0.1:11435`. Proxies and redirects are disabled. No public API, device target, runtime starter or model weights are bundled. Only one inference task runs through this client's lock at a time; coordinate other clients separately.

## Tests

```bash
cargo test --locked --manifest-path tools/local-review/Cargo.toml
```

Tests exercise input-path restrictions, job IDs, model restrictions and incomplete/truncated/successful streams, without a server. Test artifacts are written beneath the ignored state directory. Stop a separately launched foreground Ollama server with Ctrl+C; this client does not manage that service.
