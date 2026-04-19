"""
Hifz Master V2 router — Wird-based Quran memorization with 7-tier SRS.

Endpoints:
  GET    /student/hifz/v2/wird/today           — Compose today's Wird
  POST   /student/hifz/v2/wird/start           — Start (or resume) Wird
  PATCH  /student/hifz/v2/wird/{id}/complete   — Complete Wird session
  POST   /student/hifz/v2/exercises/answer     — Submit exercise answer
  POST   /student/hifz/v2/steps/result         — Submit step result
  GET    /student/hifz/v2/surah/{n}/content    — Enriched surah content
  GET    /student/hifz/v2/map                  — Journey map
  GET    /student/hifz/v2/verse/{surah}/{verse}/progress — Verse progress V2
"""
import json
import uuid
import logging
from pathlib import Path
from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import StudentUser, DB
from ..schemas.hifz_v2 import (
    WirdTodayOut, WirdBlocOut, WirdVerseInfo,
    WirdStartRequest, WirdSessionOut, WirdCompleteRequest,
    ExerciseAnswerRequest, ExerciseAnswerOut,
    StepResultRequest, StepResultOut,
    EnrichedSurahOut,
    JourneyMapOut, SurahMapEntry,
    VerseProgressV2Out,
)
from ..models.hifz_v2 import SRS_TIERS, tier_from_score
from ..models.hifz_master import VerseProgress
from ..services.hifz_v2_service import (
    compose_wird, start_wird, complete_wird,
    process_exercise_answer, process_step_result,
    build_journey_map, calculate_stars,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/hifz/v2", tags=["Hifz Master V2"])

# Path to enriched surah JSON data
DATA_DIR = Path(__file__).parent.parent / "data"


# ══════════════════════════════════════════════════════════════════
# Wird Endpoints
# ══════════════════════════════════════════════════════════════════

@router.get("/wird/today", response_model=WirdTodayOut)
def get_wird_today(student: StudentUser, db: DB):
    """
    Compose today's Wird (daily session).

    Returns JADID (new), QARIB (recent review), BA'ID (distant review)
    blocs with verse info and estimated duration.
    """
    from ..models.hifz_v2 import WirdSession, WirdStatus

    today = date.today()

    # Check for existing session
    existing = (
        db.query(WirdSession)
        .filter(
            WirdSession.student_id == student.id,
            WirdSession.date == today,
        )
        .first()
    )

    composition = compose_wird(db, student.id)

    # Build bloc outputs
    blocs = []

    if composition["jadid_verses"]:
        blocs.append(WirdBlocOut(
            bloc_type="JADID",
            label_ar="جديد",
            verses=[
                WirdVerseInfo(
                    surah_number=v["surah_number"],
                    verse_number=v["verse_number"],
                )
                for v in composition["jadid_verses"]
            ],
        ))

    if composition["qarib_verses"]:
        blocs.append(WirdBlocOut(
            bloc_type="QARIB",
            label_ar="قريب",
            verses=[
                WirdVerseInfo(
                    surah_number=v["surah_number"],
                    verse_number=v["verse_number"],
                    mastery_score=v.get("mastery_score", 0),
                    srs_tier=v.get("srs_tier", 1),
                )
                for v in composition["qarib_verses"]
            ],
        ))

    if composition["baid_verses"]:
        blocs.append(WirdBlocOut(
            bloc_type="BAID",
            label_ar="بعيد",
            verses=[
                WirdVerseInfo(
                    surah_number=v["surah_number"],
                    verse_number=v["verse_number"],
                    mastery_score=v.get("mastery_score", 0),
                    srs_tier=v.get("srs_tier", 1),
                )
                for v in composition["baid_verses"]
            ],
        ))

    total_verses = (
        len(composition["jadid_verses"])
        + len(composition["qarib_verses"])
        + len(composition["baid_verses"])
    )

    session_status = "NOT_STARTED"
    session_id = None
    progress = 0

    if existing:
        session_id = existing.id
        session_status = existing.status.value
        if existing.status == WirdStatus.COMPLETED:
            progress = 100
        elif total_verses > 0:
            # Approximate progress from exercises done
            progress = min(95, int((existing.total_exercises / max(1, total_verses * 3)) * 100))

    return WirdTodayOut(
        wird_session_id=session_id,
        date=today,
        blocs=blocs,
        estimated_duration_minutes=composition["estimated_minutes"],
        total_verses=total_verses,
        reciter_folder=composition["reciter_folder"],
        status=session_status,
        progress_percent=progress,
    )


@router.post("/wird/start", response_model=WirdSessionOut, status_code=status.HTTP_201_CREATED)
def start_wird_session(student: StudentUser, db: DB):
    """
    Start (or resume) today's Wird session.

    Creates a new WirdSession if none exists for today.
    Returns existing session if already started.
    """
    wird = start_wird(db, student.id)
    db.commit()
    db.refresh(wird)
    return WirdSessionOut.model_validate(wird)


@router.patch("/wird/{wird_id}/complete", response_model=WirdSessionOut)
def complete_wird_session(
    wird_id: uuid.UUID,
    body: WirdCompleteRequest,
    student: StudentUser,
    db: DB,
):
    """
    Mark a Wird session as completed.

    Awards completion XP and updates streak.
    """
    try:
        wird = complete_wird(
            db, student.id, wird_id,
            body.duration_seconds, body.total_exercises, body.correct_exercises,
        )
        db.commit()
        db.refresh(wird)
        return WirdSessionOut.model_validate(wird)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ══════════════════════════════════════════════════════════════════
# Exercise & Step Endpoints
# ══════════════════════════════════════════════════════════════════

@router.post("/exercises/answer", response_model=ExerciseAnswerOut)
def submit_exercise_answer(body: ExerciseAnswerRequest, student: StudentUser, db: DB):
    """
    Submit an exercise answer.

    Updates mastery score, SRS tier, and awards XP.
    Returns before/after scores and stars.
    """
    result = process_exercise_answer(
        db=db,
        student_id=student.id,
        surah_number=body.surah_number,
        verse_number=body.verse_number,
        exercise_type_str=body.exercise_type,
        is_correct=body.is_correct,
        wird_session_id=body.wird_session_id,
        response_time_ms=body.response_time_ms,
        attempt_number=body.attempt_number,
        metadata=body.metadata,
    )
    db.commit()
    return ExerciseAnswerOut(**result)


@router.post("/steps/result", response_model=StepResultOut)
def submit_step_result(body: StepResultRequest, student: StudentUser, db: DB):
    """
    Submit a step result (NOUR, TIKRAR, TAMRIN, TASMI, NATIJA).

    Blends step score into verse mastery using weighted average.
    """
    result = process_step_result(
        db=db,
        student_id=student.id,
        surah_number=body.surah_number,
        verse_number=body.verse_number,
        step=body.step,
        score=body.score,
        duration_seconds=body.duration_seconds,
        wird_session_id=body.wird_session_id,
        metadata=body.metadata,
    )
    db.commit()
    return StepResultOut(**result)


# ══════════════════════════════════════════════════════════════════
# Enriched Content Endpoints
# ══════════════════════════════════════════════════════════════════

@router.get("/surah/{surah_number}/content", response_model=EnrichedSurahOut)
def get_surah_content(surah_number: int, student: StudentUser, db: DB):
    """
    Get enriched surah content for the Wird flow.

    Returns verses with Arabic text, French translation, context,
    word list, audio timings, and key words.

    Falls back to basic content from DB if enriched JSON not available.
    """
    from ..models.quran import Surah

    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Numéro de sourate invalide")

    # Try to load from enriched JSON file first
    json_path = DATA_DIR / "juz_amma_enriched.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                all_surahs = json.load(f)

            for s in all_surahs:
                if s.get("surah_number") == surah_number:
                    return EnrichedSurahOut(**s)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading enriched surah data: %s", e)

    # ── Fallback: use Quran text JSON + DB metadata ────────────────
    surah = db.query(Surah).filter(Surah.surah_number == surah_number).first()
    if not surah:
        raise HTTPException(
            status_code=404,
            detail=f"Sourate {surah_number} non trouvée"
        )

    # Load real Arabic text from quran_juz_amma_text.json
    quran_text = {}
    quran_text_path = DATA_DIR / "quran_juz_amma_text.json"
    if quran_text_path.exists():
        try:
            with open(quran_text_path, "r", encoding="utf-8") as f:
                quran_text = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading Quran text data: %s", e)

    surah_text_data = quran_text.get(str(surah_number), {})
    surah_verses = surah_text_data.get("verses", {})

    verses = []
    for v_num in range(1, surah.total_verses + 1):
        text_ar = surah_verses.get(str(v_num), f"﴿ آية {v_num} ﴾")
        verses.append({
            "number": v_num,
            "text_ar": text_ar,
            "words": text_ar.split(),
        })

    logger.info(
        "Fallback content for surah %d (%s) — %d verses (from quran text JSON)",
        surah_number, surah.surah_name_ar, surah.total_verses,
    )

    return EnrichedSurahOut(
        surah_number=surah_number,
        name_ar=surah.surah_name_ar,
        name_fr=surah.surah_name_fr,
        name_transliteration=surah.surah_name_en,
        revelation="mecquoise" if surah.is_meccan else "médinoise",
        verse_count=surah.total_verses,
        theme_fr="",
        intro_fr="",
        verses=verses,
    )


# ══════════════════════════════════════════════════════════════════
# Journey Map & Progress
# ══════════════════════════════════════════════════════════════════

@router.get("/map", response_model=JourneyMapOut)
def get_journey_map(student: StudentUser, db: DB):
    """
    Get the journey map with all surah progress.

    Shows Juz Amma (78-114) with verse counts, mastery, stars.
    """
    data = build_journey_map(db, student.id)
    return JourneyMapOut(
        surahs=[SurahMapEntry(**s) for s in data["surahs"]],
        total_verses_memorized=data["total_verses_memorized"],
        total_stars=data["total_stars"],
        current_streak=data["current_streak"],
        total_xp=data["total_xp"],
        level=data["level"],
        title_ar=data["title_ar"],
        title_fr=data["title_fr"],
    )


@router.get("/verse/{surah_number}/{verse_number}/progress", response_model=VerseProgressV2Out)
def get_verse_progress_v2(
    surah_number: int,
    verse_number: int,
    student: StudentUser,
    db: DB,
):
    """
    Get V2 progress for a specific verse.

    Returns mastery score, SRS tier with label/color, stars, review info.
    """
    verse_prog = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student.id,
            VerseProgress.surah_number == surah_number,
            VerseProgress.verse_number == verse_number,
        )
        .first()
    )

    if not verse_prog:
        # Return default (new verse)
        tier = tier_from_score(0)
        tier_info = SRS_TIERS[tier]
        return VerseProgressV2Out(
            surah_number=surah_number,
            verse_number=verse_number,
            mastery_score=0,
            srs_tier=tier.value,
            srs_tier_label=tier_info["label_fr"],
            srs_tier_color=tier_info["color"],
            stars=0,
            next_review_date=date.today(),
            review_count=0,
        )

    score = verse_prog.mastery_score
    tier = tier_from_score(score)
    tier_info = SRS_TIERS[tier]

    # Count exercises for this verse
    from ..models.hifz_v2 import VerseExercise
    exercise_count = (
        db.query(VerseExercise)
        .filter(
            VerseExercise.student_id == student.id,
            VerseExercise.surah_number == surah_number,
            VerseExercise.verse_number == verse_number,
        )
        .count()
    )

    return VerseProgressV2Out(
        surah_number=surah_number,
        verse_number=verse_number,
        mastery_score=score,
        srs_tier=tier.value,
        srs_tier_label=tier_info["label_fr"],
        srs_tier_color=tier_info["color"],
        stars=calculate_stars(score),
        next_review_date=verse_prog.next_review_date,
        review_count=verse_prog.review_count,
        total_exercises_played=exercise_count,
        last_practiced_at=verse_prog.last_practiced_at,
    )


# ══════════════════════════════════════════════════════════════════
# Export router
# ══════════════════════════════════════════════════════════════════
hifz_v2_router = router
