"""K-rewrite sampling for GRPO: rewrite via rewriter-llm, score via frozen base 7B."""

from __future__ import annotations

import argparse
import atexit
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from plugins.parallel_k_rewrite import generate_k_parallel_rewrites
from plugins.text_description_evaluator.design_text_evaluator_api import (
    DesignTextEvaluator,
    JudgeConnectionError,
    is_connection_failure,
    load_default_evaluator,
)
from training.record_builder import rewrite_error_of
from training.build_grpo_source_corpus import DEFAULT_OUT as DEFAULT_CORPUS
from training.jsonl_logger import TrainingRunLogger
from training.record_builder import sha256_text

SCRIPT_MARKER = "collect_k_rewrite_samples.py"
COMPLETED_NAME = "completed_groups.txt"
PID_NAME = "collect.pid"


def _load_corpus(path: Path, *, roles: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if roles and rec.get("role") not in roles:
                continue
            rows.append(rec)
            if limit > 0 and len(rows) >= limit:
                break
    return rows


def _inject_original_as_candidate(
    evaluator: DesignTextEvaluator,
    parallel_result: Dict[str, Any],
    source_text: str,
    *,
    source_name: str,
) -> None:
    """Keep the unrevised draft in the group as a low-reward contrast (negatives)."""
    ev = evaluator.evaluate_text(source_text, source_name=source_name)
    cands = list(parallel_result.get("candidates") or [])
    cands.append(
        {
            "candidate_index": -1,
            "text": source_text,
            "temperature": 0.0,
            "dedupe_kept": True,
            "evaluation": ev,
            "error": None,
            "injected_original": True,
        }
    )
    parallel_result["candidates"] = cands


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except SystemError:
        return False
    return True


def _kill_pid(pid: int) -> None:
    if pid <= 0 or pid == os.getpid() or not _pid_alive(pid):
        return
    print(f"killing previous collect pid={pid}")
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
        )
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return
    for _ in range(30):
        if not _pid_alive(pid):
            return
        time.sleep(0.1)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def _cmdline_of(pid: int) -> str:
    proc_cmd = Path("/proc") / str(pid) / "cmdline"
    if proc_cmd.is_file():
        try:
            return proc_cmd.read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace")
        except OSError:
            return ""
    return ""


def _iter_other_collect_pids() -> List[int]:
    my = os.getpid()
    found: Set[int] = set()
    proc = Path("/proc")
    if proc.is_dir():
        for entry in proc.iterdir():
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == my:
                continue
            cmd = _cmdline_of(pid)
            if SCRIPT_MARKER in cmd:
                found.add(pid)
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", SCRIPT_MARKER],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for token in out.split():
            try:
                pid = int(token)
            except ValueError:
                continue
            if pid != my and SCRIPT_MARKER in (_cmdline_of(pid) or SCRIPT_MARKER):
                found.add(pid)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return sorted(found)


def _kill_previous_collectors(pid_path: Path) -> None:
    victims: Set[int] = set()
    if pid_path.is_file():
        try:
            old = int(pid_path.read_text(encoding="utf-8").strip().split()[0])
            if old != os.getpid() and _pid_alive(old):
                victims.add(old)
        except (ValueError, OSError):
            pass
    victims.update(_iter_other_collect_pids())
    for pid in sorted(victims):
        _kill_pid(pid)
    time.sleep(0.3)


def _write_pidfile(pid_path: Path) -> None:
    pid_path.write_text(str(os.getpid()) + "\n", encoding="utf-8")

    def _cleanup() -> None:
        try:
            if pid_path.is_file() and pid_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                pid_path.unlink()
        except OSError:
            pass

    atexit.register(_cleanup)


def _load_completed(path: Path) -> Set[str]:
    if not path.is_file():
        return set()
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def _append_completed(path: Path, source_id: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(source_id + "\n")
        f.flush()
        os.fsync(f.fileno())


def _rewrite_completed(path: Path, keep: Set[str]) -> None:
    kept: List[str] = []
    seen: Set[str] = set()
    if path.is_file():
        for ln in path.read_text(encoding="utf-8").splitlines():
            sid = ln.strip()
            if sid and sid in keep and sid not in seen:
                seen.add(sid)
                kept.append(sid)
    path.write_text(("\n".join(kept) + "\n") if kept else "", encoding="utf-8")


def _connection_error_text(err: Any) -> Optional[str]:
    if err is None:
        return None
    if is_connection_failure(err):
        return str(err)
    return None


def _first_connection_error_from_result(result: Dict[str, Any]) -> Optional[str]:
    for cand in result.get("candidates") or []:
        text = _connection_error_text(cand.get("error"))
        if text:
            return text
    return None


def _connection_failed_group_ids(jsonl: Path) -> Set[str]:
    bad: Set[str] = set()
    if not jsonl.is_file():
        return bad
    with jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            if _connection_error_text(rewrite_error_of(rec)):
                gid = str(rec.get("group_id") or "")
                if gid:
                    bad.add(gid)
    return bad


def _purge_groups(jsonl: Path, completed_path: Path, drop: Set[str]) -> int:
    """Delete exception groups from samples.jsonl and completed_groups.txt."""
    if not drop:
        return 0
    keep = {gid for gid in _group_ids_in_order(jsonl) if gid not in drop}
    dropped = _rewrite_jsonl_keep_groups(jsonl, keep)
    done = _load_completed(completed_path)
    _rewrite_completed(completed_path, done - drop)
    return dropped


def _group_ids_in_order(jsonl: Path) -> List[str]:
    order: List[str] = []
    seen: Set[str] = set()
    if not jsonl.is_file():
        return order
    with jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            gid = str(rec.get("group_id") or "")
            if gid and gid not in seen:
                seen.add(gid)
                order.append(gid)
    return order


def _rewrite_jsonl_keep_groups(jsonl: Path, keep: Set[str]) -> int:
    """Drop in-progress groups; return number of lines removed."""
    if not jsonl.is_file():
        return 0
    tmp = jsonl.with_suffix(".jsonl.tmp")
    dropped = 0
    with jsonl.open("r", encoding="utf-8") as src, tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            raw = line.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            gid = str(rec.get("group_id") or "")
            if gid in keep:
                dst.write(raw + "\n")
            else:
                dropped += 1
    os.replace(tmp, jsonl)
    return dropped


def _bootstrap_completed(jsonl: Path, completed_path: Path) -> Set[str]:
    """Resume set: sidecar if present; else all groups except the last jsonl group (may be partial)."""
    done = _load_completed(completed_path)
    bad = _connection_failed_group_ids(jsonl)
    if bad:
        n_drop = _purge_groups(jsonl, completed_path, bad)
        done -= bad
        print(
            f"purged {len(bad)} connection-failed groups "
            f"({n_drop} jsonl rows) from {jsonl.name}"
        )
    if done:
        dropped = _rewrite_jsonl_keep_groups(jsonl, done)
        if dropped:
            print(f"dropped {dropped} in-progress jsonl rows not in {completed_path.name}")
        return done
    order = _group_ids_in_order(jsonl)
    if not order:
        return set()
    done = set(order[:-1])
    if done:
        completed_path.write_text("\n".join(sorted(done)) + "\n", encoding="utf-8")
        dropped = _rewrite_jsonl_keep_groups(jsonl, done)
        print(
            f"bootstrapped {len(done)} completed groups; "
            f"will redo last group {order[-1]!r} (dropped {dropped} rows)"
        )
    else:
        print(f"incomplete first group {order[-1]!r}; will redo from start of jsonl")
        jsonl.write_text("", encoding="utf-8")
    return done


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    p.add_argument("--run-id", type=str, default="grpo_chanel_inverse_v1")
    p.add_argument("--k", type=int, default=None)
    p.add_argument("--limit", type=int, default=0, help="0 = all sources")
    p.add_argument("--roles", type=str, default="positive,negative")
    p.add_argument("--start", type=int, default=0)
    p.add_argument(
        "--no-inject-original-negatives",
        action="store_true",
        help="Do not add the original negative draft as an extra group member",
    )
    p.add_argument(
        "--no-kill-previous",
        action="store_true",
        help="Do not kill an already-running collect_k_rewrite_samples.py",
    )
    p.add_argument(
        "--no-resume",
        action="store_true",
        help="Do not skip sources already in completed_groups.txt",
    )
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=REPO / "plugins" / "text_description_evaluator" / "fashion_sys_prompt.txt",
    )
    args = p.parse_args()
    inject_neg = not args.no_inject_original_negatives
    roles = [x.strip() for x in args.roles.split(",") if x.strip()]
    corpus = _load_corpus(args.corpus, roles=roles, limit=0)
    corpus = corpus[args.start :]
    if args.limit > 0:
        corpus = corpus[: args.limit]
    if not corpus:
        raise SystemExit(f"no sources in {args.corpus}")

    sys_hash = None
    if args.system_prompt_file.is_file():
        sys_hash = sha256_text(args.system_prompt_file.read_text(encoding="utf-8"))

    logger = TrainingRunLogger(args.run_id)
    pid_path = logger.run_dir / PID_NAME
    completed_path = logger.run_dir / COMPLETED_NAME

    if not args.no_kill_previous:
        _kill_previous_collectors(pid_path)
    _write_pidfile(pid_path)

    done: Set[str] = set()
    if not args.no_resume:
        done = _bootstrap_completed(logger.path(), completed_path)

    pending = [src for src in corpus if str(src.get("source_id") or "") not in done]
    print(
        f"run_dir={logger.run_dir} jsonl={logger.path()} "
        f"n_sources={len(corpus)} already_done={len(done)} pending={len(pending)}"
    )
    if not pending:
        print("nothing to do")
        return

    evaluator = load_default_evaluator()
    n_pending = len(pending)
    for i, src in enumerate(pending, start=1):
        sid = str(src.get("source_id") or f"src_{i}")
        text = str(src.get("text") or "").strip()
        biz = str(src.get("business_context") or "")
        role = str(src.get("role") or "")
        print(f"[{i}/{n_pending}] {role} {sid}", flush=True)
        try:
            result = generate_k_parallel_rewrites(
                text,
                k=args.k,
                evaluator=evaluator,
                group_id=sid,
                extra_context=biz,
            )
            if inject_neg and role == "negative":
                _inject_original_as_candidate(
                    evaluator,
                    result,
                    text,
                    source_name=f"{sid}.original",
                )
            conn_err = _first_connection_error_from_result(result)
            if conn_err:
                raise JudgeConnectionError(conn_err)
        except JudgeConnectionError as exc:
            drop = _connection_failed_group_ids(logger.path())
            drop.add(sid)
            n_drop = _purge_groups(logger.path(), completed_path, drop)
            raise SystemExit(
                f"connection failure on {sid}; aborted collection and "
                f"deleted {n_drop} exception record(s) in {drop}"
            ) from exc
        logger.append_parallel_result(
            result,
            context={
                "shared_source_text": text,
                "business_context": biz,
                "source_role": role,
                "source_path": src.get("path"),
                "instruction_summary": "Rewrite the look into a grounded T2I fashion prompt.",
                "system_prompt_label": "fashion_sys_prompt.txt",
            },
            system_prompt_sha256=sys_hash,
        )
        _append_completed(completed_path, sid)
    print("done", logger.path())


if __name__ == "__main__":
    main()
