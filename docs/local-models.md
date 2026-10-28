# Local model

The documented local model is **Qwen3 32B**, `qwen3:32b`, Q4_K_M, served through Ollama. Weights and runtime are not included. See the [official model entry](https://ollama.com/library/qwen3:32b).

## Client configuration

The Rust client uses fixed loopback HTTP and disables proxies and redirects. These settings describe the included client, not general Ollama defaults.

| Setting | Included client behavior |
| --- | --- |
| Endpoint | Fixed `http://127.0.0.1:11435` |
| Model | `qwen3:32b`; optional `ONR_LOCAL_MODEL` must have this exact value |
| Context and output | 4,096 context tokens; at most 1,024 output tokens |
| Input | At most 2,048 combined UTF-8 bytes of prompt and evidence |
| Inference | Batch size 64; thinking disabled |
| Deadlines | 3-second connection timeout; 540-second request timeout |
| Residency | Request specifies `keep_alive: "10m"` |
| Concurrency | One inference task per client state-directory lock |

Settings are bound into saved task identities where implemented. This lock does not coordinate unrelated Ollama clients. The client does not start or stop the server.

## Optional inference setup

Inference requires Ollama installed separately and substantial memory and disk capacity; model download uses network bandwidth and many gigabytes of storage. Confidential input requires a locally controlled service. The offline submit and test examples do not require a server or weights.

For an isolated local server, use a separate terminal:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

In another terminal, download the model only if needed:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3:32b
```

Then use the [Rust inference example](../tools/local-review/README.md). Stop the foreground server with Ctrl+C when finished. These setup/inference commands were not run while preparing this repository; server availability, memory capacity and upstream behavior are environment-dependent.

Model answers are untrusted text requiring review. The client saves requests, partial responses and results locally. Failed or interrupted jobs are not automatically replayed. Inputs must be reviewed UTF-8 files within this repository; path filters are an accidental-inclusion guard, not comprehensive secret detection.

Local extraction and review reduced the need to send bulk material to the hosted assistant; no measured quota saving or universal performance claim is made. Public configuration does not reconstruct every historical model task.
