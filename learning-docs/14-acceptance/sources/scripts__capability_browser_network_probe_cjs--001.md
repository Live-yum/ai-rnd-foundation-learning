# scripts/capability_browser_network_probe.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_browser_network_probe.；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/capability_browser_network_probe.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L103。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4829`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_browser_network_probe.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4333e78423ad57953cde78af9e6d4518ba37f19a45ff71dee61a1e506b925a60"} -->
````javascript
// scripts/capability_browser_network_probe.cjs
// Trusted live namespace/resource probe, not an application acceptance report.
const fs = require('node:fs')
const net = require('node:net')
const os = require('node:os')
const dgram = require('node:dgram')
const assert = require('node:assert/strict')
const {spawn} = require('node:child_process')

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
  process.stdout.write(JSON.stringify({passed:true, kernel_resource_limits:true, network_none:true, tmpfs_exhaustion:true, pid_exhaustion:true, readonly_root:true}))
}
module.exports = {requireNoRoute, requireReadOnly}
if (require.main === module) main().catch(() => {process.exitCode=1})
````
