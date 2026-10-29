# Static JavaScript inventory

This tool inspects saved JavaScript without executing device responses.

Requires Node.js 22.x (22.18+) or 24.11+ and npm. Run from the repository root:

```bash
npm ci --ignore-scripts --prefix tools/js-inventory
node tools/js-inventory/inventory.cjs tools/js-inventory/fixtures/sample.js
npm test --prefix tools/js-inventory
```

Installation downloads the pinned Babel parser and its locked dependencies from npm. The first inventory returns JSON containing the synthetic `Profile` function and `profiles` and `token` declarations. `token` is reported as empty. Literal strings, numbers and booleans are not emitted; string lengths are retained. The fixture's deliberate exception is not executed.

A reviewed local JavaScript filename can replace the fixture path. Inputs over 2 MiB or invalid JavaScript fail with a nonzero exit code. HTML wrappers and module syntax are not supported; supply a standalone classic script. No input is imported, evaluated or sent to the network by this utility.

This is a shape inventory, not a secret scanner or JavaScript interpreter. Top-level declarations only are summarized; dynamic expressions remain syntax-node types, and destructuring uses a pattern marker. It does not establish dataflow, backend authorization or constructor semantics. Names, locations and shape metadata can still be sensitive: review output before sharing. Avoid untrusted enormous or deeply nested inputs despite the file-size guard.

## Output and troubleshooting

The JSON has `constructors` and `variables` arrays. Despite its name, `constructors` lists named top-level function declarations; constructor usage is not established by this classification. Variables include source lines and initializer shapes. A string reports length and whether it is empty, rather than its contents.

- A missing `@babel/parser` error means dependencies are unavailable; run the installation command above from the repository root.
- A parse error can indicate invalid JavaScript, an HTML wrapper or module syntax. Provide a reviewed standalone classic script; do not execute it to diagnose the error.
- `Input exceeds 2 MiB limit` means the file is too large. Prepare a smaller standalone input rather than increasing the guard blindly.
- CLI failures print an `inventory:` error and return a nonzero exit code.
