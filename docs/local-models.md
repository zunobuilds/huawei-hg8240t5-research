# Local model

The documented local model is **Qwen3 32B**, `qwen3:32b`, Q4_K_M, served through Ollama. Weights and runtime are not included. See the [official model entry](https://ollama.com/library/qwen3:32b).

The Rust client uses fixed loopback HTTP at `127.0.0.1:11435`, disables proxies and redirects, and accepts only this model name. Defaults are 4,096 context tokens, 2,048 bytes of combined input, 1,024 output tokens, batch size 64, thinking disabled and a 540-second request deadline. One client inference task holds a local lock at a time.

## Optional inference setup

Inference requires Ollama installed separately and substantial memory and disk capacity; model download uses network bandwidth and many gigabytes of storage. Do not send confidential input to a service you do not control. The offline submit and test examples do not require a server or weights.

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
