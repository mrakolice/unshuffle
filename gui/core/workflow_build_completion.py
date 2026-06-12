from __future__ import annotations

import logging

from . import workflow_session_persistence


def merge_pending_skipped_duplicates(res: dict, skipped: dict | None) -> None:
    for key, value in (skipped or {}).items():
        res.setdefault(key, value)


def apply_default_move_flag(res: dict, options: dict | None) -> None:
    opts = options or {}
    res.setdefault("move", bool(opts.get("move", res.get("move", True))))


def _move_committed_count(res: dict) -> int:
    copied = int(res.get("copied", 0) or 0)
    fallback_copies = int(res.get("fallback_copies", 0) or 0)
    return max(0, copied - fallback_copies)


def display_committed_count(res: dict) -> int:
    if res.get("move"):
        return _move_committed_count(res)
    return int(res.get("copied", 0) or 0)


def apply_retry_display_counts(res: dict, options: dict | None) -> None:
    opts = options or {}
    if "display_total" not in opts:
        return
    base = int(opts.get("display_committed_base", 0) or 0)
    res["display_total"] = int(opts.get("display_total", res.get("total", 0)) or 0)
    res["display_committed"] = base + display_committed_count(res)
    res["display_attempt_total"] = int(res.get("total", 0) or 0)


def retry_display_context(res: dict, options: dict | None) -> dict:
    opts = options or {}
    total = int(res.get("display_total", opts.get("display_total", res.get("total", 0))) or 0)
    committed = int(res.get("display_committed", display_committed_count(res)) or 0)
    return {
        "display_total": total,
        "display_committed_base": committed,
    }


def committed_record_count(res: dict) -> int:
    return int(res.get("copied", 0) or 0) + int(res.get("duplicates", 0) or 0)


def build_session_id(res: dict, engine) -> str:
    return str((res.get("session_id") if isinstance(res, dict) else "") or getattr(engine, "session_id", "") or "")


def prune_successful_build_state(engine) -> None:
    if not engine or not getattr(engine, "db", None):
        return
    try:
        keep_sid = {engine.session_id} if getattr(engine, "session_id", None) else set()
        engine.db.prune_ephemeral_state(
            keep_sid,
            target_root=engine.target_dir,
            use_restorable_fallback=False,
        )
    except Exception:
        logging.debug("Post-build stale staging cleanup skipped.", exc_info=True)


def persist_build_session(settings, engine, session_id: str) -> None:
    try:
        workflow_session_persistence.persist_build_session(settings, engine, session_id)
    except Exception:
        logging.exception("Failed to persist launcher settings after build.")


def invalidate_build_history_cache(engine, committed_count: int) -> None:
    if not committed_count:
        return
    try:
        from ..utils.history import invalidate_history_cache

        invalidate_history_cache(str(engine.target_dir))
    except Exception:
        logging.debug("Build history cache invalidation skipped.", exc_info=True)
