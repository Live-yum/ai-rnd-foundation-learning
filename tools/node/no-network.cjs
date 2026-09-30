// Fail closed for network APIs used by these trusted local tools. Not a hostile-JS sandbox.
const deny = () => { throw new Error('RND local tool network access is disabled'); };
const net = require('node:net');
net.connect = net.createConnection = deny;
net.Socket.prototype.connect = deny;
require('node:tls').connect = deny;
require('node:dgram').createSocket = deny;
for (const kind of ['node:http', 'node:https']) {
  const module = require(kind); module.request = module.get = deny;
}
require('node:http2').connect = deny;
const dns = require('node:dns');
for (const key of Object.keys(dns)) {
  if (/^(lookup|resolve|reverse)/.test(key) && typeof dns[key] === 'function') dns[key] = deny;
}
for (const key of Object.keys(dns.promises)) {
  if (/^(lookup|resolve|reverse)/.test(key) && typeof dns.promises[key] === 'function') dns.promises[key] = deny;
}
globalThis.fetch = async () => deny();
require('node:module').syncBuiltinESMExports();
