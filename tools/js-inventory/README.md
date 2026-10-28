# Static JavaScript inventory

Requires Node.js 22.x (22.18+) or 24.11+ and npm. Run from the repository root:

```bash
npm ci --ignore-scripts --prefix tools/js-inventory
node tools/js-inventory/inventory.cjs tools/js-inventory/fixtures/sample.js
npm test --prefix tools/js-inventory
```

Installation downloads the pinned Babel parser and its locked dependencies from npm. The first inventory returns JSON containing the synthetic `Profile` constructor and `profiles` and `token` declarations. `token` is reported as empty. Literal strings, numbers and booleans are not emitted; string lengths are retained. The fixture's deliberate exception is not executed.

For your own reviewed file, pass one local JavaScript filename in place of the fixture. Inputs over 2 MiB or invalid JavaScript fail with a nonzero exit code. HTML wrappers and module syntax are not supported; supply a standalone classic script. No input is imported, evaluated or sent to the network by this utility.

This is a shape inventory, not a secret scanner or JavaScript interpreter. Top-level declarations only are summarized; dynamic expressions remain syntax-node types, and destructuring uses a pattern marker. It does not establish dataflow, backend authorization or constructor semantics. Names, locations and shape metadata can still be sensitive: review output before sharing. Avoid untrusted enormous or deeply nested inputs despite the file-size guard.
