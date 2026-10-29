# Methodology and evidence limits

I investigated a retired device on an isolated management LAN. Playwright handled WebUI interactions; device actions were supervised, sequential and logged. This repository contains offline tools only; preparing these documents did not resume diagnostics.

## Evidence workflow

1. Record scope and intended actions before collection.
2. Save observations and request results with context.
3. Parse saved JavaScript as data without executing device responses.
4. Compare authenticated and anonymous behavior using controls and separate browser contexts.
5. Check consequential model claims against source, syntax trees, photographs or request evidence.
6. Record failed attempts and corrections, then report verified conclusions and limits.

The collection contained 24 distinct menu snapshots, 222 response records, 89 verified unique blobs and 97 text files. Three transient response bodies were unavailable. These figures describe a WebUI corpus, not firmware extraction, filesystem access or distinct vulnerability counts.

## AI assistance

Codex supported orchestration, code and writing; local models handled focused extraction, review and summaries. I did not measure a percentage saving in hosted usage. The public local-model setup is described in [local-models.md](local-models.md); historical tasks are not all attributed to that setup.

Source and request checks exposed unsupported model inferences that needed correction or rejection. Examples include treating cryptographic keywords elsewhere in the UI as an explanation for an opaque field, or drawing conclusions from incomplete transport evidence. AI output alone does not establish a vulnerability. Not every generated statement is certified as independently validated.

## Boundaries

No resets, reboots, flashing, persistent service changes or backdoor installation were authorized in the current workflow. I did not confirm a Linux shell or arbitrary command execution. An earlier benign ping diagnostic left normal test values in the interface; the original blank/default fields were not restored. A blanket claim that the project never submitted any diagnostic input would therefore be inaccurate.

I keep raw captures and identifying values private. Photographic mosaics are resampled combinations with alignment limits, not calibrated measurements or recovered hidden detail. Public single-frame photo copies are described separately in [hardware](hardware.md).
