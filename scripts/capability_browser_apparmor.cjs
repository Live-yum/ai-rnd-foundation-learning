// Read the kernel's actual current label before any candidate/browser work.
const fs = require('node:fs')
function requireAppArmor(api = fs) {
  const fd = api.openSync('/proc/self/attr/current', 'r')
  const buffer = Buffer.alloc(128)
  try {
    const size = api.readSync(fd, buffer, 0, buffer.length, 0)
    const label = buffer.subarray(0, size)
    if (!label.equals(Buffer.from('docker-default (enforce)')) && !label.equals(Buffer.from('docker-default (enforce)\n'))) {
      throw new Error('worker_apparmor_not_enforced')
    }
  } finally { api.closeSync(fd) }
  return true
}
module.exports = {requireAppArmor}
