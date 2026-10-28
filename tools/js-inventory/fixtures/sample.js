// Entirely synthetic. This is parsed, not executed.
function Profile(label, enabled, secret) {}
var profiles = [new Profile('example', true, 'SYNTHETIC_SECRET_DO_NOT_EMIT')];
var token = '';
throw new Error('Input scripts must never execute');
