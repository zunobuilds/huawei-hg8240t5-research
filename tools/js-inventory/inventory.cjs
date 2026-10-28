// Parse saved JavaScript as data. Never evaluate or import input scripts.
const fs = require('node:fs');
const {parse} = require('@babel/parser');

function shape(node) {
  if (!node) return {type: 'Missing'};
  if (node.type === 'NullLiteral') return {type: node.type, empty: true};
  if (node.type === 'StringLiteral') return {type: node.type, empty: node.value === '', length: node.value.length};
  if (['NumericLiteral', 'BooleanLiteral', 'BigIntLiteral'].includes(node.type)) return {type: node.type};
  if (node.type === 'ArrayExpression') return {type: node.type, count: node.elements.length, elements: node.elements.map(shape)};
  if (node.type === 'NewExpression') return {
    type: node.type,
    constructor: node.callee.type === 'Identifier' ? node.callee.name : '[expression]',
    arguments: node.arguments.map(shape)
  };
  return {type: node.type};
}

function inventory(code) {
  const ast = parse(code, {sourceType: 'script', errorRecovery: false});
  const constructors = ast.program.body.filter(n => n.type === 'FunctionDeclaration' && n.id).map(n => ({
    name: n.id.name,
    parameters: n.params.map(p => p.type === 'Identifier' ? p.name : '[pattern]')
  }));
  const variables = ast.program.body.filter(n => n.type === 'VariableDeclaration').flatMap(n => n.declarations.map(d => ({
    name: d.id.type === 'Identifier' ? d.id.name : '[pattern]',
    line: d.loc.start.line,
    value: shape(d.init)
  })));
  return {constructors, variables};
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 1) throw new Error('Usage: node inventory.cjs SAVED_SCRIPT.js');
    if (fs.statSync(args[0]).size > 2 * 1024 * 1024) throw new Error('Input exceeds 2 MiB limit');
    console.log(JSON.stringify(inventory(fs.readFileSync(args[0], 'utf8')), null, 2));
  } catch (e) { console.error(`inventory: ${e.message}`); process.exitCode = 1; }
}
module.exports = {inventory};
