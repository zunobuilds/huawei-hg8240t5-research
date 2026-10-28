const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {inventory} = require('./inventory.cjs');

test('reports shapes without literal values and does not execute input', () => {
  const result = inventory(fs.readFileSync(path.join(__dirname, 'fixtures/sample.js'), 'utf8'));
  assert.deepEqual(result.constructors[0].parameters, ['label', 'enabled', 'secret']);
  assert.equal(result.variables[0].value.elements[0].constructor, 'Profile');
  assert.equal(result.variables[1].value.empty, true);
  assert.ok(!JSON.stringify(result).includes('SYNTHETIC_SECRET_DO_NOT_EMIT'));
});
test('invalid syntax fails instead of reporting an empty inventory', () => {
  assert.throws(() => inventory('var = broken'));
});
test('dynamic expressions remain expressions', () => {
  const result = inventory('var x = obtainSecret(); var n = null; var a = new Array(1, 2);');
  assert.deepEqual(result.variables[0].value, {type: 'CallExpression'});
  assert.equal(result.variables[1].value.empty, true);
  assert.equal(result.variables[2].value.constructor, 'Array');
});
