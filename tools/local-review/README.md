# Local file review

I adapted this Linux Rust client from the private file-review workflow. It saves deduplicated tasks, streams answers and never executes model output. Requires Rust/Cargo 1.99 or later. Run from the repository root; first compilation may download dependencies and runs Cargo dependency build scripts.

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

## Troubleshooting

- **Input too large:** the prompt and all evidence together must fit within 2,048 UTF-8 bytes. Split the task into focused reviewed packets; this is a byte limit, not a token limit.
- **Private/cache/state inputs excluded:** prepare a separate reviewed input in an allowed repository path. Do not rename a credential file merely to bypass the filter.
- **Connection failure or missing model:** `submit`, `status` and tests work without inference. For `ask` or `run`, check the separate [model setup](../../docs/local-models.md) and fixed loopback port.
- **Worker holds the lock:** let that task finish or inspect it before intervening. `recover ID` obtains the lock and only changes a saved `running` record to `interrupted`; it does not stop a process or retry inference.
- **Failed or interrupted task:** inspect its saved input, state and partial output. Submit a deliberately revised prompt to create a new task; do not expect `ask` to replay an unchanged failed task.
- **Checkout moved:** rebuild the client; its repository root is embedded at compilation.

For the only supported model override and inference defaults, see [local-model configuration](../../docs/local-models.md). The path guard does not replace review of input contents.
