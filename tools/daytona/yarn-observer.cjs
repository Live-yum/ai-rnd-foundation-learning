// Yarn's supported hook observes manifest scripts, not implicit shell builds.
// No dependency commands, environments, paths, output or network URLs are read.
let plugin;
module.exports = {
  name: "rnd-build-observer",
  factory(require) {
    if (plugin) return plugin;
    const { YarnVersion } = require("@yarnpkg/core");
    const { createHash, randomBytes } = require("node:crypto");
    const session = randomBytes(8).toString("hex");
    const { writeSync } = require("node:fs");
    const { spawnSync } = require("node:child_process");
    const names = new Set([
      "@nestjs/core", "@swc/core", "esbuild", "sharp", "msw", "nx",
      "core-js", "sqlite3", "@parcel/watcher", "protobufjs", "@scarf/scarf",
      "unrs-resolver", "cpu-features", "core-js-pure",
    ]);
    const version = value => typeof value === "string" && /^\d{1,5}\.\d{1,5}\.\d{1,5}$/.test(value) ? value : "unknown";
    const active = new Map();
    let started = 0, completed = 0, overflow = false;
    const now = () => Number(process.hrtime.bigint() / 1000000000n);
    const emit = value => {
      try { writeSync(1, "RND_BUILD_OBSERVATION " + JSON.stringify({session, ...value}) + "\n"); } catch {}
    };
    let corepack = "unknown";
    try {
      const result = spawnSync("corepack", ["--version"], {
        timeout: 2000, killSignal: "SIGKILL", maxBuffer: 1024,
        stdio: ["ignore", "pipe", "ignore"],
      });
      if (result.status === 0) corepack = version(result.stdout.toString().trim());
    } catch {}
    const tools = { event: "tools", node: version(process.versions.node), yarn: version(YarnVersion), corepack,
      coverage: "manifest_scripts_only" };
    emit(tools);
    const snapshot = () => { emit(tools); emit({
      event: "pending", started, completed, active_count: active.size, overflow,
      scripts: [...active.values()].slice(0, 32).map(({ since, ...item }) => ({
        ...item, state: "awaiting_script_exit", elapsed_seconds: Math.min(2400, now() - since),
      })),
    }); };
    const timer = setInterval(snapshot, 30000);
    timer.unref();
    return plugin = { hooks: {
      async wrapScriptExecution(executor, project, locator, scriptName) {
        if (!["preinstall", "install", "postinstall"].includes(scriptName)) return executor;
        return async () => {
          if (started >= 256) { overflow = true; return await executor(); }
          const pkg = project.storedPackages.get(locator.locatorHash);
          const name = pkg && (pkg.scope ? "@" + pkg.scope + "/" : "") + pkg.name;
          const id = createHash("sha256").update(String(locator.locatorHash)).digest("hex");
          const item = { id, package: names.has(name) ? name : "other", version: version(pkg?.version), script: scriptName };
          const key = ++started;
          active.set(key, { ...item, since: now() });
          emit({ event: "start", ...item });
          let state = "threw", exit_code = null;
          try {
            const result = await executor();
            state = "returned";
            exit_code = Number.isInteger(result) && result >= 0 && result <= 255 ? result : null;
            return result;
          } finally {
            completed++;
            active.delete(key);
            emit({ event: "end", ...item, state, exit_code });
            if (active.size === 0) snapshot();
          }
        };
      },
      afterAllInstalled() { snapshot(); },
    } };
  },
};
