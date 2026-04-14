"""
XP Service — Experience points and level calculation.

Level formula: threshold(n) = 50 * n² + 50
Scoring table:
  QCM:        base 5,  +2 if <5s,  N/A hints,   range 3-7 XP
  REORDER:    base 10, +3 if <8s,  -3/hint,     range 5-13 XP
  FILL_BLANK: base 15, +5 if <10s, -5/hint,     range 5-20 XP
  TRANSLATE:  base 25, +8 if <20s, -8/hint,     range 9-33 XP
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from uuid import UUID

from ..models.gamification import XPEvent
from ..models.user import User


def calculate_level(total_xp: int) -> int:
    """Calculate level from total XP. Formula: threshold(n) = 50*n² + 50"""
    level = 0
    while True:
        threshold = 50 * (level + 1) ** 2 + 50
        if total_xp < threshold:
            break
        level += 1
    return max(1, level)


def xp_for_next_level(total_xp: int) -> dict:
    """Calculate XP needed for next level."""
    current_level = calculate_level(total_xp)
    current_threshold = 50 * current_level ** 2 + 50 if current_level > 0 else 0
    next_threshold = 50 * (current_level + 1) ** 2 + 50
    return {
        "current_level": current_level,
        "total_xp": total_xp,
        "current_threshold": current_threshold,
        "next_threshold": next_threshold,
        "xp_in_level": total_xp - current_threshold,
        "xp_needed": next_threshold - total_xp,
    }


def award_xp(
    db: DBSession,
    student_id: UUID,
    source: str,
    xp_amount: int,
    source_id: str | None = None,
) -> dict:
    """Award XP to a student and update their level."""
    if xp_amount <= 0:
        return {"xp_earned": 0, "level_up": False}

    # Record XP event
    event = XPEvent(
        student_id=student_id,
        source=source,
        source_id=source_id,
        xp_earned=xp_amount,
    )
    db.add(event)

    # Update user totals
    user = db.query(User).filter_by(id=student_id).first()
    if not user:
        return {"xp_earned": 0, "level_up": False}

    old_level = user.level
    user.total_xp += xp_amount
    user.level = calculate_level(user.total_xp)

    db.flush()

    return {
        "xp_earned": xp_amount,
        "total_xp": user.total_xp,
        "level": user.level,
        "level_up": user.level > old_level,
    }


def calculate_quiz_xp(correct: int, total: int, time_ms: int) -> int:
    """Calculate XP for a quiz submission. Base 5 per correct, +2 bonus if fast."""
    base = correct * 5
    avg_time_per_q = time_ms / max(total, 1)
    speed_bonus = 2 * correct if avg_time_per_q < 5000 else 0  # <5s per question
    return max(0, base + speed_bonus)


def calculate_drill_xp(
    drill_type: str,
    is_correct: bool,
    time_ms: int,
    hints_used: int = 0,
) -> int:
    """Calculate XP for a drill exercise."""
    if not is_correct:
        return 0

    SCORING = {
        "QCM":        {"base": 5,  "speed_bonus": 2, "speed_threshold_ms": 5000,  "hint_penalty": 0},
        "REORDER":    {"base": 10, "speed_bonus": 3, "speed_threshold_ms": 8000,  "hint_penalty": 3},
        "FILL_BLANK": {"base": 15, "speed_bonus": 5, "speed_threshold_ms": 10000, "hint_penalty": 5},
        "TRANSLATE":  {"base": 25, "speed_bonus": 8, "speed_threshold_ms": 20000, "hint_penalty": 8},
    }

    config = SCORING.get(drill_type.upper(), SCORING["QCM"])
    xp = config["base"]

    if time_ms < config["speed_threshold_ms"]:
        xp += config["speed_bonus"]

    xp -= hints_used * config["hint_penalty"]

    return max(1, xp)  # Minimum 1 XP for a correct answer


def get_xp_history(db: DBSession, student_id: UUID, days: int = 30) -> list[dict]:
    """Get XP history grouped by date for the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    events = (
        db.query(
            func.date(XPEvent.created_at).label("date"),
            func.sum(XPEvent.xp_earned).label("total"),
        )
        .filter(
            XPEvent.student_id == student_id,
            XPEvent.created_at >= cutoff,
        )
        .group_by(func.date(XPEvent.created_at))
        .order_by(func.date(XPEvent.created_at))
        .all()
    )

    return [{"date": str(e.date), "xp_earned": e.total} for e in events]
