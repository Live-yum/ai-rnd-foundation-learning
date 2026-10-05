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
