// Trusted live namespace/resource probe, not an application acceptance report.
const fs = require('node:fs')
const net = require('node:net')
const os = require('node:os')
const dgram = require('node:dgram')
const assert = require('node:assert/strict')
const {spawn, spawnSync} = require('node:child_process')

async function requireNoRoute(host, port, connect = options => net.connect(options)) {
  return await new Promise((resolve, reject) => {
    const socket = connect({host, port})
    socket.setTimeout(750)
    socket.on('connect', () => { socket.destroy(); reject(new Error('unexpected_network_route')) })
    socket.on('error', error => {
      socket.destroy()
      // Refused connections, name failures and timeout do not prove isolation.
      if (error.code === 'ENETUNREACH') resolve()
      else reject(new Error('network_denial_not_proven'))
    })
    socket.on('timeout', () => { socket.destroy(); reject(new Error('network_denial_not_proven')) })
  })
}

function requireReadOnly(api = fs, uid = process.getuid()) {
  const path = '/opt/readonly-probe'
  const stat = api.lstatSync(path)
  assert(stat.isDirectory() && stat.uid === uid && (stat.mode & 0o777) === 0o700)
  // This directory is owned and writable by the worker in the image. Only
  // EROFS demonstrates the read-only mount; EACCES is not accepted as proof.
  assert.throws(() => api.writeFileSync(path + '/write-probe', 'denied'), error => error.code === 'EROFS')
}

async function main() {
  const apparmor = process.env.CAPABILITY_BROWSER_REQUIRE_APPARMOR === '1'
  if (apparmor) require('./capability_browser_apparmor.cjs').requireAppArmor()
  assert.equal(process.arch, 'x64')
  assert.equal(process.platform, 'linux')
  assert.equal(require('playwright/package.json').version, '1.56.1')
  const executable = require('playwright').chromium.executablePath()
  const executableFd = fs.openSync(executable, 'r')
  const elf = Buffer.alloc(64)
  try { assert.equal(fs.readSync(executableFd, elf, 0, 64, 0), 64) }
  finally { fs.closeSync(executableFd) }
  assert.equal(elf.subarray(0, 4).toString('hex'), '7f454c46')
  assert.equal(elf[4], 2) // ELFCLASS64
  assert.equal(elf[5], 1) // little endian
  assert.equal(elf.readUInt16LE(18), 62) // EM_X86_64
  const version = spawnSync(executable, ['--version'], {encoding:'utf8', timeout:10000, maxBuffer:4096})
  assert.equal(version.status, 0)
  assert.equal(version.stdout.trim(), 'Chromium 141.0.7390.37')
  assert.equal(process.getuid(), 1000)
  assert.equal(process.getgid(), 1000)
  const status = Object.fromEntries(fs.readFileSync('/proc/self/status','utf8').trim().split('\n').map(line => {
    const colon = line.indexOf(':'); return [line.slice(0, colon), line.slice(colon + 1).trim()]
  }))
  assert.equal(status.NoNewPrivs, '1')
  assert.equal(status.Seccomp, '2')
  for (const name of ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']) assert.equal(BigInt('0x' + status[name]), 0n)
  assert.equal(fs.readFileSync('/sys/fs/cgroup/memory.max','utf8').trim(), '805306368')
  assert.equal(fs.readFileSync('/sys/fs/cgroup/pids.max','utf8').trim(), '128')
  assert.equal(fs.readFileSync('/sys/fs/cgroup/cpu.max','utf8').trim(), '100000 100000')
  assert.deepEqual(fs.readdirSync('/sys/class/net').sort(), ['lo'])
  const interfaces = os.networkInterfaces()
  assert.deepEqual(Object.keys(interfaces).sort(), ['lo'])
  assert(interfaces.lo.every(address => address.internal))
  assert(fs.readFileSync('/proc/net/route', 'utf8').trim().split('\n').length === 1)
  for (const [host, port] of [['169.254.169.254',80],['172.17.0.1',2375],['1.1.1.1',443],['2001:db8::1',443]]) {
    await requireNoRoute(host, port)
  }
  // Prove a working namespace-local TCP stack rather than relying on a list
  // of unrelated closed host ports as supposed network isolation evidence.
  const local = net.createServer(socket => socket.end())
  await new Promise((resolve, reject) => {
    local.once('error', reject)
    local.listen(0, '127.0.0.1', resolve)
  })
  try {
    await new Promise((resolve, reject) => {
      const socket = net.connect({host:'127.0.0.1', port:local.address().port})
      socket.once('connect', () => { socket.destroy(); resolve() })
      socket.once('error', reject)
    })
  } finally { await new Promise(resolve => local.close(resolve)) }
  await new Promise((resolve, reject) => {
    const socket = dgram.createSocket('udp4')
    let closed = false
    const finish = error => {
      if (closed) return
      closed = true
      socket.close()
      if (error && error.code === 'ENETUNREACH') resolve()
      else reject(new Error('udp_denial_not_proven'))
    }
    socket.once('error', finish)
    socket.send(Buffer.from('probe'), 53, '1.1.1.1', finish)
  })
  requireReadOnly()
  let bounded = false
  const fd = fs.openSync('/tmp/budget-probe','w')
  try { for (let i = 0; i < 160; i++) fs.writeSync(fd, Buffer.alloc(1024 * 1024)) }
  catch (e) { bounded = e.code === 'ENOSPC' }
  finally { fs.closeSync(fd); fs.unlinkSync('/tmp/budget-probe') }
  assert(bounded)
  const children = []
  let pidDenied = false
  try {
    for (let i = 0; i < 140; i++) {
      const ok = await new Promise(resolve => {
        const child = spawn('/bin/sleep', ['30'], {stdio:'ignore'})
        child.once('spawn', () => {children.push(child); resolve(true)})
        child.once('error', e => {pidDenied = e.code === 'EAGAIN'; resolve(false)})
      })
      if (!ok) break
    }
  } finally { for (const child of children) child.kill('SIGKILL') }
  assert(pidDenied)
  process.stdout.write(JSON.stringify({passed:true, kernel_resource_limits:true, network_none:true, tmpfs_exhaustion:true, pid_exhaustion:true, readonly_root:true, browser_build:true, ...(apparmor ? {apparmor_enforced:true} : {})}))
}
module.exports = {requireNoRoute, requireReadOnly}
if (require.main === module) main().catch(() => {process.exitCode=1})
