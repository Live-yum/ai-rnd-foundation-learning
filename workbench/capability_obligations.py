"""Source-bound, explicitly reviewed atomic contracts and independent storage checks.

The human review is the semantic boundary: it approves the relevance and exhaustive
decomposition of an exact source. Execution proves only those frozen assertions,
not arbitrary natural language. Neither model reviews nor application reports can
create this approval or a physical witness.
"""

import json
import re
import uuid

from workbench.capability_isolation import CONTROL, control_exec
from workbench.capability_verification import CheckFailure, interpolate, json_equal
from workbench.domain import digest

PROTOCOL = "reviewed-source-obligations-v1"


def obligation_identity(obligation):
    return digest({"protocol": PROTOCOL, "contract": obligation.model_dump()})


def review_contract(plan, policy):
    return {
        "protocol": PROTOCOL,
        "plan_digest": digest(plan.model_dump()),
        "policy_digest": digest(policy),
        "source_digest": policy["source_digest"],
        "obligations": [o.model_dump() for o in plan.obligations],
        "complete_source_ids": plan.complete_source_ids,
        "meaning": "Explicitly review each source binding and whether its atomic assertions are exhaustive; runtime evidence alone does not decide this.",
    }


SQLITE_PROBE = r"""
import json,os,pathlib,re,sqlite3,stat,sys,tempfile,time,urllib.parse
if sys.platform.startswith('linux'):
 import resource
 resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024))
 resource.setrlimit(resource.RLIMIT_CPU,(3,3))
 resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024*1024,64*1024*1024))
root=pathlib.Path('/tmp/rnd-capability/product')
private=pathlib.Path('/tmp/rnd-module-control/private')
control_uid=0
request_path=pathlib.Path(sys.argv[1])
assert request_path.parent==private and re.fullmatch(r'obligation-[a-f0-9]{32}\.json',request_path.name)
directory=os.open(private,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 owner=os.fstat(directory)
 assert owner.st_uid==control_uid and stat.S_IMODE(owner.st_mode)&0o077==0
 source=os.open(request_path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=directory)
 try:
  owner=os.fstat(source)
  assert stat.S_ISREG(owner.st_mode) and owner.st_nlink==1 and owner.st_uid==control_uid
  assert stat.S_IMODE(owner.st_mode)&0o022==0 and 0<owner.st_size<=65536
  with os.fdopen(source,'rb',closefd=False) as stream:raw=stream.read(65537)
  assert len(raw)<=65536
 finally:os.close(source)
finally:os.close(directory)
payload=json.loads(raw)
assert type(payload) is dict and set(payload)=={'database_path','assertion'}
relative=pathlib.PurePosixPath(payload['database_path'])
assert not relative.is_absolute() and relative.parts and all(p not in {'.','..'} for p in relative.parts)
request=payload['assertion']
# Pin each directory and file without following links. SQLite only sees a
# controller-private copy, never a path that the candidate can rename/replace.
# This is required even with quiescence: SIGSTOP alone is not a filesystem
# security boundary against a hostile sibling attempting SIGCONT races.
flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
parent=os.open('/',flags)
try:
 for component in (*root.parts[1:],*relative.parts[:-1]):
  following=os.open(component,flags,dir_fd=parent)
  os.close(parent);parent=following
 with tempfile.TemporaryDirectory(prefix='sqlite-observation-',dir=private) as temporary:
  snapshot=pathlib.Path(temporary)/'observation.db';budget=128*1024*1024
  for suffix in ('','-wal','-journal'):
   try:source=os.open(relative.name+suffix,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
   except FileNotFoundError:
    assert suffix
    continue
   try:
    before=os.fstat(source)
    assert stat.S_ISREG(before.st_mode) and before.st_nlink==1
    assert 0<=before.st_size<=64*1024*1024 and before.st_size<=budget
    # Never let SQLite interpret a candidate rollback/super-journal path or
    # perform recovery. Committed WAL and absent/empty DELETE journals suffice.
    if suffix=='-journal':
     assert before.st_size==0
     continue
    budget-=before.st_size
    with open(str(snapshot)+suffix,'xb') as target:
     remaining=before.st_size
     while remaining:
      block=os.read(source,min(remaining,65536));assert block
      target.write(block);remaining-=len(block)
     assert not os.read(source,1)
    after=os.fstat(source)
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
   finally:os.close(source)
  with sqlite3.connect('file:'+urllib.parse.quote(str(snapshot))+'?mode=ro',uri=True,timeout=2) as c:
   c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA query_only=ON')
   end=time.monotonic()+3;c.set_progress_handler(lambda:time.monotonic()>end,1000)
   c.execute('BEGIN')
   row=c.execute('SELECT type,sql FROM sqlite_schema WHERE name=?',(request['table'],)).fetchone()
   assert row and row[0]=='table' and row[1].lstrip().upper().startswith('CREATE TABLE')
   cols=list(request['values']);keys=list(request['key'])
   physical={name for name,hidden in c.execute('SELECT name,hidden FROM pragma_table_xinfo(?)',(request['table'],)) if hidden==0}
   assert set(cols+keys)<=physical
   query='SELECT '+','.join('physical."'+name+'"' for name in cols)+' FROM "'+request['table']+'" AS physical WHERE '+' AND '.join('physical."'+name+'"=?' for name in keys)+' LIMIT 2'
   rows=c.execute(query,[request['key'][key] for key in keys]).fetchall()
   data=[dict(zip(cols,row)) for row in rows]
   encoded=json.dumps(data);assert len(encoded.encode())<=65536;print(encoded)
finally:os.close(parent)
"""


def assert_physical_rows(rows, assertion):
    if type(rows) is not list or len(rows) != 1 or not json_equal(rows[0], assertion["values"]):
        raise CheckFailure("原子业务义务的独立物理值不符；固定响应或无关表写入不能关闭义务")


def run_obligation_checks(sandbox, plan, scenarios, saved, timeout, *, phase):
    """System interpreter reads SQLite as data. Candidate code is never imported."""
    if phase not in {"initial", "restart"}:
        raise CheckFailure("未知业务义务验证阶段")
    relevant = {scenario.id for scenario in scenarios}
    obligations = [o for o in plan.obligations if o.scenario_id in relevant]
    if obligations and plan.selection.database != "sqlite":
        raise CheckFailure("当前声明式物理义务仅支持SQLite；原生PostgreSQL须使用登记的独立oracle")
    if obligations and phase == "initial":
        # The first observation may drain the app because no requests remain
        # before its required restart. The restart observation instead pauses
        # and resumes that same new process, before any replay can rebuild rows.
        from workbench.capability_sandbox import restart_application_identity

        restart_application_identity(sandbox, plan.runtime.port, timeout)
    result = []
    for obligation in obligations:
        variables = saved.get(obligation.scenario_id)
        if not isinstance(variables, dict):
            raise CheckFailure("原子业务义务缺少同次场景的独立捕获值")
        assertion = {
            "table": obligation.physical.table,
            "key": interpolate(obligation.physical.key, variables),
            "values": interpolate(obligation.physical.values, variables),
        }
        # Revalidate after interpolation. Captured strings cannot add SQL, paths,
        # collections or unbounded output; all values become bound parameters.
        from workbench.capability_contracts import PhysicalAssertion

        try:
            PhysicalAssertion.model_validate(assertion)
            encoded = json.dumps(
                {"database_path": plan.runtime.database_path, "assertion": assertion},
                ensure_ascii=False,
            ).encode()
            if len(encoded) > 65536:
                raise ValueError("probe input budget")
        except ValueError:
            raise CheckFailure("原子业务义务插值超出有界数据合同") from None
        request_path = CONTROL + "/private/obligation-" + uuid.uuid4().hex + ".json"
        argv = [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            SQLITE_PROBE,
            request_path,
        ]
        probe_timeout = min(timeout, 10)
        if phase == "restart":
            from workbench.settings import ROOT

            probe_timeout = min(timeout, 15)
            if probe_timeout <= 2:
                raise CheckFailure("重启物理义务探针缺少安全暂停及恢复的时间预算")
            supervisor = (ROOT / "scripts/capability_sqlite_quiescence.py").read_text()
            argv[4] = supervisor
            argv.extend([str(min(probe_timeout - 2, 12)), SQLITE_PROBE])
        # /proc/*/cmdline is readable by the app even for root commands. Never
        # put the challenge in argv, shell source or environment, including
        # before the supervisor freezes the app. The FS API transports bytes
        # directly into the already protected root-only control directory.
        try:
            sandbox.fs.upload_file(encoded, request_path, timeout=probe_timeout)
            observed = control_exec(sandbox, argv, probe_timeout)
        finally:
            cleanup = control_exec(
                sandbox, ["/usr/bin/rm", "-f", "--", request_path], min(timeout, 5)
            )
            if cleanup.exit_code != 0:
                raise CheckFailure("独立物理义务的私有请求清理未确认")
        try:
            if observed.exit_code or len(observed.result.encode()) > 65536:
                raise ValueError("probe failed")
            rows = json.loads(observed.result)
        except ValueError, TypeError, AttributeError:
            raise CheckFailure("独立物理义务探针失败，未接受应用自报结果") from None
        assert_physical_rows(rows, assertion)
        result.append(
            {
                "id": obligation.id,
                "contract_sha256": obligation_identity(obligation),
                "phase": phase,
                "passed": True,
                "observation_sha256": digest({"key": assertion["key"], "rows": rows}),
            }
        )
    return result


def require_obligation_evidence(plan, proof, *, aggregate):
    expected = {
        (o.id, phase): obligation_identity(o)
        for o in plan.obligations
        for phase in (("initial", "restart") if aggregate else ("initial",))
    }
    rows = proof.get("obligation_checks", [])
    if not isinstance(rows, list):
        raise CheckFailure("原子业务义务证据格式无效")
    actual = {}
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"id", "contract_sha256", "phase", "passed", "observation_sha256"}
            or row.get("passed") is not True
            or not re.fullmatch(r"[a-f0-9]{64}", str(row.get("observation_sha256", "")))
        ):
            raise CheckFailure("原子业务义务证据不完整")
        key = (row["id"], row["phase"])
        if key in actual:
            raise CheckFailure("原子业务义务证据重复")
        actual[key] = row["contract_sha256"]
    if actual != expected:
        raise CheckFailure("缺少与当前来源/场景绑定的独立物理义务证据")
    if aggregate:
        values = {(row["id"], row["phase"]): row["observation_sha256"] for row in rows}
        if any(values[o.id, "initial"] != values[o.id, "restart"] for o in plan.obligations):
            raise CheckFailure("重启后原子业务物理值已改变")


def reviewed_coverage(plan, policy, proof, approval, base):
    """Called only after runtime proof and durable local-operator approval checks."""
    if not plan.obligations:
        return base
    if approval.get("contract_digest") != digest(review_contract(plan, policy)) or (
        approval.get("actor") != "local-operator"
    ):
        raise CheckFailure("原子业务来源及完整性声明缺少当前明确人工审阅")
    require_obligation_evidence(plan, proof, aggregate=True)
    rows = [dict(row) for row in base["obligations"]]
    closed = set(plan.complete_source_ids)
    # External prerequisites remain open regardless of semantic approval.
    closed -= {source for p in plan.prerequisites for source in p.requirements}
    for row in rows:
        if row["semantic"] == "original.full_source" and row["source_id"] in closed:
            row["status"] = "verified"
            row["evidence_basis"] = PROTOCOL
    rows.extend(
        {
            "goal_id": obligation_identity(o),
            "source_id": o.source_id,
            "source_sha256": o.source_sha256,
            "semantic": o.assertion,
            "status": "verified",
            "evidence_basis": PROTOCOL,
        }
        for o in plan.obligations
    )
    sources = {row["source_id"] for row in rows}
    return {
        **base,
        "obligations": rows,
        "complete_source_ids": sorted(closed),
        "remaining_source_ids": sorted(sources - closed),
        "remaining_obligations": [row["goal_id"] for row in rows if row["status"] != "verified"],
        "full_request_complete": bool(sources) and closed == sources,
        "coverage_level": "operator-reviewed-atomic-contracts",
        "semantic_review": approval,
        "natural_language_semantics_proven": False,
    }
