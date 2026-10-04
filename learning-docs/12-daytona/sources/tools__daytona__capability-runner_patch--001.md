# tools/daytona/capability-runner.patch · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-runner.patch`；**本文件共有 1 段**。本段覆盖源文件 L1–L35。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1355`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-runner.patch", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c2809b3517062208709b9800082b5465de67c3c2d795f22c4842d564d4a89c12"} -->
````text
# tools/daytona/capability-runner.patch
--- a/apps/runner/pkg/docker/container_configs.go
+++ b/apps/runner/pkg/docker/container_configs.go
@@ -198,11 +198,9 @@
 	}
 
 	hostConfig := &container.HostConfig{
-		// Privileged mode exposes every /dev/nvidia* node and bypasses the
-		// CDI cgroup rules, so GPU sandboxes have to opt out to keep their
-		// allocated card isolated. Non-GPU sandboxes still need privileged
-		// for their current workloads.
-		Privileged: gpuIndex == nil,
+		// Owned fixed-application profile: all application containers use
+		// Docker's unprivileged defaults, including its default seccomp filter.
+		Privileged: false,
 		Binds:      binds,
 	}
 
@@ -234,6 +232,17 @@
 		}
 	}
 
+	// Custom-source executions get bounded writable storage on ordinary runners.
+	// Root control remains distinct; Landlock confines every product write here.
+	if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {
+		pidLimit := int64(256)
+		hostConfig.PidsLimit = &pidLimit
+		hostConfig.Tmpfs = map[string]string{"/tmp": "rw,nosuid,nodev,size=1073741824,mode=1777"}
+		if strings.HasPrefix(sandboxDto.Name, "rnd-source-native-") {
+			pidLimit = 384
+			hostConfig.Tmpfs = map[string]string{"/tmp": "rw,nosuid,nodev,size=4294967296,mode=1777"}
+		}
+	}
 	containerRuntime := config.GetContainerRuntime()
 	if containerRuntime != "" {
 		hostConfig.Runtime = containerRuntime
````
