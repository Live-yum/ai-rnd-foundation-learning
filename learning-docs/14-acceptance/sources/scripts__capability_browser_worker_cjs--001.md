# scripts/capability_browser_worker.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_browser_worker.；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/capability_browser_worker.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L67。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3031`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_browser_worker.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0c599895446e316dc21353046a51d5a2c96e69d802e603c73b7c41ec31023a33"} -->
````javascript
// scripts/capability_browser_worker.cjs
// Trusted stdio relay; no candidate code, credentials, or host mounts are loaded.
const http = require('node:http')
const readline = require('node:readline')
const {spawn} = require('node:child_process')
const MAX = 4 * 1024 * 1024
let child, server, count = 0, active = 0, contract, report = Buffer.alloc(0)
const pending = new Map()
const lines = readline.createInterface({input: process.stdin})
function fail() { if (child) child.kill('SIGKILL'); process.exit(1) }
function emit(value) { process.stdout.write(JSON.stringify(value) + '\n') }
process.on('uncaughtException', fail)
process.on('unhandledRejection', fail)
setTimeout(fail, 180000).unref()
lines.on('line', line => {
  if (line.length > 6 * 1024 * 1024) return fail()
  const value = JSON.parse(line)
  if (!contract) {
    contract = value
    server = http.createServer((req, res) => {
      if (++active > 8) return fail()
      const chunks = []
      let size = 0
      req.on('data', data => { size += data.length; if (size > MAX) fail(); chunks.push(data) })
      req.on('end', () => {
        if (++count > 256) return fail()
        const id = count
        const headers = {}
        for (const k of ['accept','content-type','cookie','authorization','x-csrf-token']) {
          if (typeof req.headers[k] === 'string') headers[k] = req.headers[k]
        }
        // Ordered IDs must reflect emission order, not request arrival order.
        pending.set(id, res)
        emit({type:'request', id, method:req.method, path:req.url, headers,
              body:Buffer.concat(chunks).toString('base64')})
      })
      req.on('error', fail)
      res.on('close', () => {active--})
    })
    server.on('upgrade', (_req, socket) => socket.destroy())
    server.requestTimeout = 5000
    server.headersTimeout = 5000
    server.maxHeadersCount = 32
    server.listen(18080, '127.0.0.1', () => {
      child = spawn(process.execPath, ['/opt/verifier/capability_browser.cjs'], {
        env: {PATH:'/usr/local/bin:/usr/bin:/bin', HOME:'/tmp', TMPDIR:'/tmp',
              PRODUCT_VERIFY_PLAYWRIGHT:'/opt/verifier/node_modules/playwright', PLAYWRIGHT_BROWSERS_PATH:'/ms-playwright'},
        stdio:['pipe','pipe','ignore'],
      })
      child.stdin.end(JSON.stringify(contract))
      child.stdout.on('data', data => {
        report = Buffer.concat([report, data]); if (report.length > 100000) fail()
      })
      child.on('error', fail)
      child.on('exit', code => {
        emit({type:'report', report:JSON.parse(report.toString()), exit_code:code})
        server.closeAllConnections(); server.close(); lines.close(); process.stdin.destroy()
      })
    })
  } else {
    if (value.type !== 'response' || !pending.has(value.id)) return fail()
    const res = pending.get(value.id); pending.delete(value.id)
    const body = Buffer.from(value.body, 'base64')
    if (body.length > MAX) return fail()
    res.writeHead(value.status, value.headers.flat()); res.end(body)
  }
})
lines.on('close', () => { if (child && child.exitCode === null) fail() })
````
