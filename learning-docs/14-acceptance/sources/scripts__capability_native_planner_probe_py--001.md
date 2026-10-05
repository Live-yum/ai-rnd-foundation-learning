# scripts/capability_native_planner_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_native_planner_probe；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_isolation`、`workbench.capability_stack`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `statements`（L55–L86）：接收`name`。 控制顺序：L56按`not re.fullmatch(r"rnd_planner_[a-f0-9]{32}", name)`分支；L57抛异常，停止当前正常路径。 调用`re.fullmatch`、`CheckFailure`。 返回路径：L86的`create, read, cleanup`。
- `verify_native_planner_identity`（L89–L131）：接收`sandbox`、`plan`、`environment`、`timeout`。 控制顺序：L90按`plan.selection.template != "fastapiadmin" or plan.selection.database != "postgresql"`分支；L91抛异常，停止当前正常路径；L106按`not app_command(create)`分支；L107抛异常，停止当前正常路径；L112按`database_counts(sandbox, count_plan, min(timeout, 15)) != {name: 1}`分支；L113抛异常，停止当前正常路径；L116按`status != 0 or output.strip() != "restricted"`分支；L117抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`CheckFailure`、`uuid.uuid4`、`statements`、`app_command`、`SimpleNamespace`、`database_counts`、`min`、`run_guarded_control`、`pg_verifier_argv`等。 返回路径：L131的`{CHECK: True}`。
- `verify_native_planner_identity.app_command`（L95–L101）：接收`sql`。 调用`run_guarded_control`、`product_argv`、`min`、`output.strip`。 返回路径：L101的`status == 0 and output.strip() == COMPLETE`。

</details>

**创建路径：** `scripts/capability_native_planner_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L131。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5591`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_native_planner_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "690bc72672dc4bad7888f0ca20075406f61c65c03bff71be6101967c59dc3ed1"} -->
````python
# scripts/capability_native_planner_probe.py
"""Harmless planner-code regression in the owned disposable PostgreSQL cluster.

No table read ever authenticates as postgres. An app-owned IMMUTABLE function
fails if a privileged reader evaluates it, and verifies that the independently
authenticated reader cannot restore an administrator role. No program execution,
private-file access, privilege mutation or external database is used.
"""

import re
import uuid
from types import SimpleNamespace

from workbench.capability_isolation import product_argv, run_guarded_control
from workbench.capability_stack import database_counts, pg_verifier_argv
from workbench.capability_verification import CheckFailure

CHECK = "postgres_planner_identity_restricted"
COMPLETE = "owned-planner-probe-command-complete"
APP_SQL = r"""
import os,selectors,subprocess,sys,time
environment={'PATH':'/usr/bin:/bin','HOME':'/nonexistent',
 'PGPASSWORD':os.environ['DATABASE_PASSWORD'],
 'PGOPTIONS':'-c search_path=pg_catalog -c statement_timeout=3000 -c lock_timeout=1000'}
# Landlock denies opening /dev/null for writing after the guard. Drain a pipe
# instead, discarding at most 4096 bytes within one deadline; never expose SQL
# diagnostics, paths, credentials or arbitrary child output to the controller.
process=None
try:
 deadline=time.monotonic()+8
 process=subprocess.Popen(['/usr/lib/postgresql/17/bin/psql','-X','-q','-At','-w',
  '-v','ON_ERROR_STOP=1','-h','127.0.0.1','-p','55432','-U','rnd_app','-d','rnd_product',
  '-c',sys.argv[1]],env=environment,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 with process.stdout,selectors.DefaultSelector() as selector:
  selector.register(process.stdout,selectors.EVENT_READ)
  remaining=4096
  while True:
   wait=deadline-time.monotonic()
   if wait<=0 or not selector.select(wait):raise TimeoutError
   chunk=os.read(process.stdout.fileno(),remaining+1)
   if not chunk:break
   remaining-=len(chunk)
   if remaining<0:raise OverflowError
  if process.wait(timeout=max(0,deadline-time.monotonic())):raise RuntimeError
except Exception:
 if process is not None:
  try:
   process.kill()
   process.wait(timeout=1)
  except Exception:pass
 raise SystemExit(1) from None
print('owned-planner-probe-command-complete')
"""


def statements(name):
    if not re.fullmatch(r"rnd_planner_[a-f0-9]{32}", name):
        raise CheckFailure("原生规划器探针身份无效")
    function = name + "_identity"
    create = f"""
CREATE TABLE public.{name}(id integer PRIMARY KEY);
INSERT INTO public.{name} VALUES(1);
CREATE FUNCTION public.{function}() RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $probe$
BEGIN
 IF current_user='postgres' OR session_user='postgres' THEN
  RAISE EXCEPTION 'privileged planner evaluation';
 END IF;
 IF current_user NOT IN ('rnd_app','rnd_verify') OR session_user NOT IN ('rnd_app','rnd_verify') THEN
  RAISE EXCEPTION 'unexpected planner identity';
 END IF;
 RETURN true;
END;
$probe$;
CREATE INDEX {name}_idx ON public.{name}(id) WHERE public.{function}();
"""
    # This explicit call guarantees evaluation even if the planner elects not
    # to examine a partial index. The physical count separately tests the real
    # production count helper against the app-owned indexed table.
    read = (
        "DO $verify$ BEGIN BEGIN EXECUTE 'SET ROLE postgres'; "
        "RAISE EXCEPTION 'unexpected administrator role transition'; "
        "EXCEPTION WHEN insufficient_privilege THEN NULL; END; END; $verify$; "
        f"SELECT CASE WHEN public.{function}() AND current_user='rnd_verify' "
        "AND session_user='rnd_verify' THEN 'restricted' ELSE 'invalid' END"
    )
    cleanup = f"DROP TABLE IF EXISTS public.{name}; DROP FUNCTION IF EXISTS public.{function}();"
    return create, read, cleanup


def verify_native_planner_identity(sandbox, plan, environment, timeout):
    if plan.selection.template != "fastapiadmin" or plan.selection.database != "postgresql":
        raise CheckFailure("规划器身份探针只允许本次独立原生PostgreSQL profile")
    name = "rnd_planner_" + uuid.uuid4().hex
    create, read, cleanup = statements(name)

    def app_command(sql):
        status, output = run_guarded_control(
            sandbox,
            product_argv(plan, ["/usr/bin/python3", "-I", "-S", "-c", APP_SQL, sql], environment),
            min(timeout, 15),
        )
        return status == 0 and output.strip() == COMPLETE

    phase = "create"
    primary_failure = "none"
    try:
        if not app_command(create):
            raise CheckFailure("应用身份无法建立有界规划器反例")
        phase = "count"
        count_plan = SimpleNamespace(
            selection=plan.selection, runtime=SimpleNamespace(database_tables=[name])
        )
        if database_counts(sandbox, count_plan, min(timeout, 15)) != {name: 1}:
            raise CheckFailure("独立低权限身份未正确读取规划器反例物理表")
        phase = "identity"
        status, output = run_guarded_control(sandbox, pg_verifier_argv(read), min(timeout, 15))
        if status != 0 or output.strip() != "restricted":
            raise CheckFailure("数据库规划器未保持独立低权限认证身份")
    except Exception:
        primary_failure = phase
        raise
    finally:
        try:
            cleaned = app_command(cleanup)
        except Exception:
            cleaned = False
        if not cleaned:
            raise CheckFailure(
                "本次规划器探针对象清理未确认，禁止交付"
                f"（primary={primary_failure}; cleanup=failed）"
            ) from None
    return {CHECK: True}
````
