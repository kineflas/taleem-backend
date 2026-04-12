"""
Hifz Master router — Gamified Quranic memorization with XP + badges.

Endpoints:
  POST   /student/hifz/goals                 — Create memorization goal
  GET    /student/hifz/goals                 — List student's goals
  GET    /student/hifz/goals/{goal_id}       — Get goal detail
  DELETE /student/hifz/goals/{goal_id}       — Delete goal

  POST   /student/hifz/sessions              — Start memorization session
  PATCH  /student/hifz/sessions/{session_id}/end — End session, calculate XP
  POST   /student/hifz/sessions/{session_id}/verse-known — Mark verse as known

  GET    /student/hifz/verses                — Get ALL memorized verses (voluntary revision)
  GET    /student/hifz/verses/due            — Get verses needing review today (SRS)
  POST   /student/hifz/verses/review         — Review a verse (success/fail)

  GET    /student/hifz/xp                    — Get student XP, level, badges
  GET    /student/hifz/heatmap/{surah_number} — Verse mastery heatmap

  GET    /student/hifz/audio/{surah_number}/{verse_number} — Audio URL builder
  GET    /student/hifz/reciters              — List available reciters
"""
import uuid
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from ..core.dependencies import CurrentUser, DB, StudentUser
from ..schemas.hifz_master import (
    HifzGoalOut, HifzGoalCreate,
    VerseProgressOut, VerseHeatmapEntry, SurahHeatmapOut,
    HifzSessionOut, HifzSessionCreate,
    StudentXPOut, BadgeOut,
    MarkVerseKnownRequest, VerseReviewRequest,
    ReciterOut,
)


# ══════════════════════════════════════════════════════════════════════════════
# Router setup
# ══════════════════════════════════════════════════════════════════════════════
router = APIRouter(prefix="/student/hifz", tags=["Hifz Master"])


from ..models.hifz_master import (
    HifzGoal, VerseProgress, HifzSession, StudentXP, StudentBadge, VerseMastery
)

# Surah verse counts (1-indexed: surah 1 = Al-Fatiha = 7 verses)
SURAH_VERSE_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99,
    128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38,
    29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18,
    12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29,
    19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8,
    11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6,
]


# ══════════════════════════════════════════════════════════════════════════════
# XP & Mastery Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def calculate_mastery_level(mastery_score: int) -> str:
    """Calculate mastery level from score (0-100)."""
    if mastery_score < 40:
        return "RED"
    elif mastery_score < 70:
        return "ORANGE"
    else:
        return "GREEN"


def get_next_review_date(mastery: str) -> date:
    """Get next review date based on mastery level."""
    today = date.today()
    if mastery == "RED":
        return today + timedelta(days=1)
    elif mastery == "ORANGE":
        return today + timedelta(days=2)
    else:  # GREEN
        return today + timedelta(days=10)


def calculate_daily_target(total_verses: int, target_date: date) -> int:
    """Calculate daily verses for TEMPORAL mode goal."""
    days_remaining = (target_date - date.today()).days
    if days_remaining <= 0:
        return total_verses
    return max(1, total_verses // days_remaining)


def award_xp(
    db: Session,
    student_id: uuid.UUID,
    xp_amount: int,
    source: str,  # "listening", "memorizing", "revision", "streaks"
) -> tuple[int, str]:  # (total_xp, new_level)
    """Award XP to student, check level thresholds, return (total, level)."""
    # TODO: Implement once StudentXP model exists
    # This is a placeholder implementation
    return (0, "DEBUTANT")


def check_and_award_badges(
    db: Session,
    student_id: uuid.UUID,
    student_xp_id: uuid.UUID,
) -> list[BadgeOut]:
    """Check if student has earned new badges based on progress."""
    # TODO: Implement once StudentBadge model exists
    return []


# ══════════════════════════════════════════════════════════════════════════════
# Goals Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/goals", response_model=HifzGoalOut, status_code=status.HTTP_201_CREATED)
def create_hifz_goal(
    body: HifzGoalCreate,
    student: StudentUser,
    db: DB,
):
    """
    Create a new memorization goal.

    Body:
      - surah_number (1-114)
      - mode: "QUANTITATIVE" or "TEMPORAL"
      - verses_per_day (required if QUANTITATIVE)
      - target_date (required if TEMPORAL)
      - reciter_id (optional, default: Alafasy_128kbps)

    For TEMPORAL mode, calculated_daily_target is auto-computed.
    """
    if body.mode == "QUANTITATIVE" and not body.verses_per_day:
        raise HTTPException(
            status_code=400,
            detail="verses_per_day required for QUANTITATIVE mode"
        )
    if body.mode == "TEMPORAL" and not body.target_date:
        raise HTTPException(
            status_code=400,
            detail="target_date required for TEMPORAL mode"
        )

    # Check unique constraint
    existing = db.query(HifzGoal).filter(
        HifzGoal.student_id == student.id,
        HifzGoal.surah_number == body.surah_number,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Un objectif pour cette sourate existe déjà"
        )

    # Get total verses for surah
    total_verses = SURAH_VERSE_COUNTS[body.surah_number - 1] if 1 <= body.surah_number <= 114 else 7

    # Calculate daily target
    daily_target = body.verses_per_day or 1
    if body.mode == "TEMPORAL" and body.target_date:
        daily_target = calculate_daily_target(total_verses, body.target_date)

    goal = HifzGoal(
        student_id=student.id,
        surah_number=body.surah_number,
        mode=body.mode,
        verses_per_day=body.verses_per_day,
        target_date=body.target_date,
        calculated_daily_target=daily_target,
        total_verses=total_verses,
        reciter_id=body.reciter_id or "Alafasy_128kbps",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    return HifzGoalOut(
        id=goal.id,
        student_id=goal.student_id,
        surah_number=goal.surah_number,
        mode=goal.mode.value,
        verses_per_day=goal.verses_per_day,
        target_date=goal.target_date,
        calculated_daily_target=goal.calculated_daily_target,
        total_verses=goal.total_verses,
        verses_memorized=goal.verses_memorized,
        is_completed=goal.is_completed,
        reciter_id=goal.reciter_id,
        started_at=goal.started_at,
        completed_at=goal.completed_at,
        updated_at=goal.updated_at,
    )


@router.get("/goals", response_model=list[HifzGoalOut])
def list_hifz_goals(student: StudentUser, db: DB):
    """List all memorization goals for the current student."""
    goals = db.query(HifzGoal).filter(
        HifzGoal.student_id == student.id
    ).order_by(HifzGoal.started_at.desc()).all()

    return [
        HifzGoalOut(
            id=g.id,
            student_id=g.student_id,
            surah_number=g.surah_number,
            mode=g.mode.value,
            verses_per_day=g.verses_per_day,
            target_date=g.target_date,
            calculated_daily_target=g.calculated_daily_target,
            total_verses=g.total_verses,
            verses_memorized=g.verses_memorized,
            is_completed=g.is_completed,
            reciter_id=g.reciter_id,
            started_at=g.started_at,
            completed_at=g.completed_at,
            updated_at=g.updated_at,
        )
        for g in goals
    ]


@router.get("/goals/{goal_id}", response_model=HifzGoalOut)
def get_hifz_goal_detail(goal_id: uuid.UUID, student: StudentUser, db: DB):
    """Get detailed goal info with verse progress."""
    goal = db.query(HifzGoal).filter(
        HifzGoal.id == goal_id,
        HifzGoal.student_id == student.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")

    return HifzGoalOut(
        id=goal.id,
        student_id=goal.student_id,
        surah_number=goal.surah_number,
        mode=goal.mode.value,
        verses_per_day=goal.verses_per_day,
        target_date=goal.target_date,
        calculated_daily_target=goal.calculated_daily_target,
        total_verses=goal.total_verses,
        verses_memorized=goal.verses_memorized,
        is_completed=goal.is_completed,
        reciter_id=goal.reciter_id,
        started_at=goal.started_at,
        completed_at=goal.completed_at,
        updated_at=goal.updated_at,
    )


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hifz_goal(goal_id: uuid.UUID, student: StudentUser, db: DB):
    """Delete a memorization goal."""
    goal = db.query(HifzGoal).filter(
        HifzGoal.id == goal_id,
        HifzGoal.student_id == student.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")
    db.delete(goal)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# Session Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/sessions", response_model=HifzSessionOut, status_code=status.HTTP_201_CREATED)
def start_hifz_session(
    body: HifzSessionCreate,
    student: StudentUser,
    db: DB,
):
    """
    Start a new memorization session.

    Body:
      - surah_number (1-114)
      - verse_start (1-286)
      - verse_end (1-286)
      - loop_count (default 5)
      - pause_seconds (default 5)
      - auto_advance (default true)
    """
    if body.verse_start > body.verse_end:
        raise HTTPException(
            status_code=400,
            detail="verse_start must be <= verse_end"
        )

    # TODO: Create and persist session once HifzSession model exists
    # session = HifzSession(
    #     student_id=student.id,
    #     surah_number=body.surah_number,
    #     loop_count=body.loop_count,
    #     pause_seconds=body.pause_seconds,
    #     auto_advance=body.auto_advance,
    #     verse_start=body.verse_start,
    #     verse_end=body.verse_end,
    # )
    # db.add(session)
    # db.commit()
    # db.refresh(session)
    # return HifzSessionOut.model_validate(session)

    return HifzSessionOut(
        id=uuid.uuid4(),
        student_id=student.id,
        goal_id=None,
        surah_number=body.surah_number,
        loop_count=body.loop_count,
        pause_seconds=body.pause_seconds,
        auto_advance=body.auto_advance,
        verse_start=body.verse_start,
        verse_end=body.verse_end,
        total_verses_practiced=0,
        verses_marked_known=0,
        duration_seconds=None,
        xp_earned=0,
        started_at=datetime.now(timezone.utc),
        ended_at=None,
    )


@router.patch("/sessions/{session_id}/end", response_model=HifzSessionOut)
def end_hifz_session(
    session_id: uuid.UUID,
    student: StudentUser,
    db: DB,
):
    """
    End a memorization session.

    - Calculates duration (ended_at - started_at)
    - Awards XP: +2 per listen, +10 per verse marked known
    - Updates student XP and level
    """
    # TODO: Implement once HifzSession model exists
    # session = db.query(HifzSession).filter(
    #     HifzSession.id == session_id,
    #     HifzSession.student_id == student.id,
    # ).first()
    # if not session:
    #     raise HTTPException(status_code=404, detail="Session not found")
    # if session.ended_at:
    #     raise HTTPException(status_code=400, detail="Session already ended")

    # now = datetime.now(timezone.utc)
    # session.ended_at = now
    # duration_secs = (now - session.started_at).total_seconds()
    # session.duration_seconds = int(duration_secs)

    # # Calculate XP
    # xp = (session.total_verses_practiced * 2) + (session.verses_marked_known * 10)
    # session.xp_earned = xp
    # total_xp, new_level = award_xp(db, student.id, xp, "listening")

    # db.commit()
    # db.refresh(session)
    # return HifzSessionOut.model_validate(session)

    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/sessions/{session_id}/verse-known", status_code=status.HTTP_200_OK)
def mark_verse_known(
    session_id: uuid.UUID,
    body: MarkVerseKnownRequest,
    student: StudentUser,
    db: DB,
):
    """
    Mark a verse as "Je le connais" (student knows it).

    - Increment verse_progress.mastery_score by 20
    - Update mastery color (RED → ORANGE → GREEN)
    - Award +10 XP for memorizing
    - Increment session.verses_marked_known
    """
    # TODO: Implement once models exist
    # session = db.query(HifzSession).filter(
    #     HifzSession.id == session_id,
    #     HifzSession.student_id == student.id,
    # ).first()
    # if not session:
    #     raise HTTPException(status_code=404, detail="Session not found")
    # if session.ended_at:
    #     raise HTTPException(status_code=400, detail="Session already ended")

    # # Get or create verse_progress
    # verse_prog = db.query(VerseProgress).filter(
    #     VerseProgress.student_id == student.id,
    #     VerseProgress.surah_number == body.surah_number,
    #     VerseProgress.verse_number == body.verse_number,
    # ).first()

    # if not verse_prog:
    #     verse_prog = VerseProgress(
    #         student_id=student.id,
    #         surah_number=body.surah_number,
    #         verse_number=body.verse_number,
    #     )
    #     db.add(verse_prog)

    # old_mastery = verse_prog.mastery
    # verse_prog.mastery_score = min(100, verse_prog.mastery_score + 20)
    # verse_prog.mastery = calculate_mastery_level(verse_prog.mastery_score)

    # # Award XP bonus if mastery changed
    # xp_bonus = 0
    # if old_mastery == "RED" and verse_prog.mastery == "ORANGE":
    #     xp_bonus = 5
    # elif old_mastery == "ORANGE" and verse_prog.mastery == "GREEN":
    #     xp_bonus = 15

    # session.verses_marked_known += 1
    # award_xp(db, student.id, 10 + xp_bonus, "memorizing")

    # db.commit()

    return {"status": "ok", "message": "Verse marked as known"}


# ══════════════════════════════════════════════════════════════════════════════
# Verse Review Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/verses", response_model=list[VerseProgressOut])
def get_all_verses(
    student: StudentUser,
    db: DB,
    limit: int = Query(200, ge=1, le=500),
):
    """
    Get ALL memorized verses for the student, regardless of review date.
    Used for voluntary revision (derniers appris / aléatoire).
    Sorted by created_at ascending — Flutter side handles sorting for each mode.
    """
    verses = (
        db.query(VerseProgress)
        .filter(VerseProgress.student_id == student.id)
        .order_by(VerseProgress.created_at.asc())
        .limit(limit)
        .all()
    )
    return [VerseProgressOut.model_validate(v) for v in verses]


@router.get("/verses/due", response_model=list[VerseProgressOut])
def get_verses_due_for_review(
    student: StudentUser,
    db: DB,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get verses needing review today (next_review_date <= today).
    Sorted by mastery priority (RED first) then by next_review_date ascending.
    """
    today = date.today()
    verses = (
        db.query(VerseProgress)
        .filter(
            and_(
                VerseProgress.student_id == student.id,
                VerseProgress.next_review_date <= today,
            )
        )
        .order_by(
            # Ordre alphabétique desc : RED > ORANGE > GREEN ✓
            VerseProgress.mastery.desc(),
            VerseProgress.next_review_date.asc(),
        )
        .limit(limit)
        .all()
    )
    return [VerseProgressOut.model_validate(v) for v in verses]


@router.post("/verses/review", response_model=VerseProgressOut)
def review_verse(
    body: VerseReviewRequest,
    student: StudentUser,
    db: DB,
):
    """
    Review a verse.

    If success=true:
      - mastery_score += 10
      - consecutive_successes++
      - Update mastery color, calculate next_review_date
      - Award +15 XP

    If success=false:
      - mastery_score = max(0, mastery_score - 15)
      - consecutive_successes = 0
      - Reset to RED, next_review_date = today
    """
    # TODO: Implement once VerseProgress model exists
    # verse_prog = db.query(VerseProgress).filter(
    #     VerseProgress.student_id == student.id,
    #     VerseProgress.surah_number == body.surah_number,
    #     VerseProgress.verse_number == body.verse_number,
    # ).first()

    # if not verse_prog:
    #     # Auto-create if doesn't exist
    #     verse_prog = VerseProgress(
    #         student_id=student.id,
    #         surah_number=body.surah_number,
    #         verse_number=body.verse_number,
    #     )
    #     db.add(verse_prog)

    # verse_prog.review_count += 1

    # if body.success:
    #     verse_prog.mastery_score = min(100, verse_prog.mastery_score + 10)
    #     verse_prog.consecutive_successes += 1
    #     award_xp(db, student.id, 15, "revision")
    # else:
    #     verse_prog.mastery_score = max(0, verse_prog.mastery_score - 15)
    #     verse_prog.consecutive_successes = 0

    # verse_prog.mastery = calculate_mastery_level(verse_prog.mastery_score)
    # verse_prog.next_review_date = get_next_review_date(verse_prog.mastery)
    # verse_prog.last_practiced_at = datetime.now(timezone.utc)

    # db.commit()
    # db.refresh(verse_prog)
    # return VerseProgressOut.model_validate(verse_prog)

    raise HTTPException(status_code=404, detail="Verse not found")


# ══════════════════════════════════════════════════════════════════════════════
# XP & Level Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/xp", response_model=StudentXPOut)
def get_student_xp(student: StudentUser, db: DB):
    """
    Get student's XP, level, and earned badges.

    Level thresholds:
      - DEBUTANT: 0-499
      - APPRENTI: 500-1999
      - HAFIZ_EN_HERBE: 2000-4999
      - HAFIZ_CONFIRME: 5000-9999
      - HAFIZ_EXPERT: 10000+
    """
    # TODO: Implement query once StudentXP model exists
    # xp_record = db.query(StudentXP).filter(
    #     StudentXP.student_id == student.id
    # ).first()

    # if not xp_record:
    #     # Auto-create if doesn't exist
    #     xp_record = StudentXP(student_id=student.id)
    #     db.add(xp_record)
    #     db.commit()
    #     db.refresh(xp_record)

    # # Fetch badges
    # badges = db.query(StudentBadge).filter(
    #     StudentBadge.student_xp_id == xp_record.id
    # ).all()

    # return StudentXPOut.model_validate(xp_record, from_attributes=True)

    return StudentXPOut(
        id=uuid.uuid4(),
        student_id=student.id,
        total_xp=0,
        level="DEBUTANT",
        xp_from_listening=0,
        xp_from_memorizing=0,
        xp_from_revision=0,
        xp_from_streaks=0,
        total_verses_memorized=0,
        total_surahs_completed=0,
        total_listening_minutes=0,
        total_sessions=0,
        badges=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# ══════════════════════════════════════════════════════════════════════════════
# Visualization Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/heatmap/{surah_number}", response_model=SurahHeatmapOut)
def get_surah_heatmap(
    surah_number: int,
    student: StudentUser,
    db: DB,
):
    """
    Get verse mastery heatmap for a surah.

    Returns all verses 1..N with their mastery level (RED/ORANGE/GREEN),
    mastery_score (0-100), and whether they need review today.
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Invalid surah number")

    # TODO: Implement once VerseProgress model exists
    # verses = db.query(VerseProgress).filter(
    #     VerseProgress.student_id == student.id,
    #     VerseProgress.surah_number == surah_number,
    # ).all()

    # today = date.today()
    # entries = []
    # for v in verses:
    #     entries.append(VerseHeatmapEntry(
    #         verse_number=v.verse_number,
    #         mastery=v.mastery,
    #         mastery_score=v.mastery_score,
    #         needs_review=v.next_review_date <= today,
    #     ))

    # return SurahHeatmapOut(surah_number=surah_number, verses=entries)

    return SurahHeatmapOut(surah_number=surah_number, verses=[])


# ══════════════════════════════════════════════════════════════════════════════
# Audio & Reciter Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/audio/{surah_number}/{verse_number}")
def get_verse_audio(
    surah_number: int,
    verse_number: int,
    current_user: CurrentUser,
    reciter: str = Query("Alafasy_128kbps"),
):
    """
    Get audio URL for a verse from EveryAyah API.

    Format: https://everyayah.com/data/{reciter}/{surah:03d}{verse:03d}.mp3

    Query: reciter (optional, default: Alafasy_128kbps)
    Returns: { "url": "..." }
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Invalid surah number")
    if verse_number < 1 or verse_number > 286:
        raise HTTPException(status_code=400, detail="Invalid verse number")

    audio_url = (
        f"https://everyayah.com/data/{reciter}/"
        f"{surah_number:03d}{verse_number:03d}.mp3"
    )

    return {"url": audio_url}


@router.get("/reciters", response_model=list[ReciterOut])
def list_reciters(current_user: CurrentUser):
    """
    List top 5 available Quranic reciters.

    Hardcoded list of popular reciters.
    """
    reciters = [
        ReciterOut(
            id="Alafasy_128kbps",
            name_ar="الشيخ مشاري راشد العفاسي",
            name_en="Mishary Rashid Alafasy",
        ),
        ReciterOut(
            id="Husary_128kbps",            # was: Al-Husary_128kbps (invalid on EveryAyah)
            name_ar="الشيخ محمود خليل الحصري",
            name_en="Mahmoud Khalil Al-Husary",
        ),
        ReciterOut(
            id="Abdul_Basit_Murattal_192kbps",  # was: Abdul_Basit_128kbps
            name_ar="الشيخ عبد الباسط عبد الصمد",
            name_en="Abdul Basit Murattal",
        ),
        ReciterOut(
            id="Menshawi_16kbps",              # was: Menshawi_128kbps
            name_ar="الشيخ محمود علي البنا",
            name_en="Mohamed Siddiq Al-Menshawi",
        ),
        ReciterOut(
            id="Shuraim_128kbps",
            name_ar="الشيخ سعود الشريم",
            name_en="Saud Al-Shuraim",
        ),
    ]

    return reciters


# ══════════════════════════════════════════════════════════════════════════════
# Export router
# ══════════════════════════════════════════════════════════════════════════════
hifz_router = router
