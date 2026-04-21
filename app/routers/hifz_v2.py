"""
Hifz Master V2 router — Wird-based Quran memorization with 7-tier SRS.

Endpoints:
  GET    /student/hifz/v2/surahs/suggested     — Suggested surahs (Ikhtiar)
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
    SuggestedSurahOut, SuggestedSurahsOut,
    CheckpointCompleteRequest, CheckpointCompleteOut,
    QuickVerifyRequest, QuickVerifyOut,
    RevisionVerseOut, AudioRevisionPlaylistOut,
)
from ..models.hifz_v2 import SRS_TIERS, tier_from_score
from ..models.hifz_master import VerseProgress
from ..services.hifz_v2_service import (
    compose_wird, start_wird, complete_wird,
    process_exercise_answer, process_step_result,
    process_checkpoint, quick_verify_surah,
    build_journey_map, calculate_stars,
    get_suggested_surahs,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/hifz/v2", tags=["Hifz Master V2"])

# Path to enriched surah JSON data
DATA_DIR = Path(__file__).parent.parent / "data"


# ══════════════════════════════════════════════════════════════════
# Wird Endpoints
# ══════════════════════════════════════════════════════════════════

@router.get("/surahs/suggested", response_model=SuggestedSurahsOut)
def get_suggested_surahs_endpoint(student: StudentUser, db: DB):
    """
    Get suggested surahs for the Ikhtiar (selection) screen.

    Returns:
      - current_surah: surah in progress (from active goal)
      - suggestions: new surahs to start
      - review_due_surahs: surahs with pending reviews
    """
    data = get_suggested_surahs(db, student.id)
    return SuggestedSurahsOut(
        current_surah=SuggestedSurahOut(**data["current_surah"]) if data["current_surah"] else None,
        suggestions=[SuggestedSurahOut(**s) for s in data["suggestions"]],
        review_due_surahs=[SuggestedSurahOut(**s) for s in data["review_due_surahs"]],
    )


@router.get("/wird/today", response_model=WirdTodayOut)
def get_wird_today(student: StudentUser, db: DB, surah_number: int | None = None):
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

    composition = compose_wird(db, student.id, surah_number=surah_number)

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
def start_wird_session(
    student: StudentUser,
    db: DB,
    body: WirdStartRequest | None = None,
):
    """
    Start (or resume) today's Wird session.

    Creates a new WirdSession if none exists for today.
    Returns existing session if already started.

    Optionally accepts surah_number to override the default goal-based surah.
    """
    surah_number = body.surah_number if body else None
    wird = start_wird(db, student.id, surah_number=surah_number)
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
# Checkpoint Endpoints (Phase 2)
# ══════════════════════════════════════════════════════════════════

@router.post("/checkpoint/complete", response_model=CheckpointCompleteOut)
def complete_checkpoint(body: CheckpointCompleteRequest, student: StudentUser, db: DB):
    """
    Complete a checkpoint verification for a group of verses.

    Updates SRS for all verses in the range and awards XP.
    """
    verse_scores = [
        {"surah_number": vs.surah_number, "verse_number": vs.verse_number, "score": vs.score}
        for vs in body.verse_scores
    ] if body.verse_scores else None

    result = process_checkpoint(
        db=db,
        student_id=student.id,
        surah_number=body.surah_number,
        verse_start=body.verse_start,
        verse_end=body.verse_end,
        tartib_score=body.tartib_score,
        takamul_score=body.takamul_score,
        tasmi_score=body.tasmi_score,
        rabita_score=body.rabita_score,
        verse_scores=verse_scores,
        duration_seconds=body.duration_seconds,
        wird_session_id=body.wird_session_id,
    )
    db.commit()
    return CheckpointCompleteOut(**result)


# ══════════════════════════════════════════════════════════════════
# Quick Verify Endpoints (Phase 3 — Mode Rapide)
# ══════════════════════════════════════════════════════════════════

@router.post("/surah/{surah_number}/quick-verify", response_model=QuickVerifyOut)
def quick_verify_surah_endpoint(
    surah_number: int,
    body: QuickVerifyRequest,
    student: StudentUser,
    db: DB,
):
    """
    Quick verification of a known surah (Mode Rapide).

    Batch-updates SRS for all verses in a single transaction.
    Used for surahs where ≥80% of verses are Tier 4+ (Acquis).
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Numéro de sourate invalide")

    verse_scores = [
        {"verse_number": vs.verse_number, "score": vs.score}
        for vs in body.verse_scores
    ]

    result = quick_verify_surah(
        db=db,
        student_id=student.id,
        surah_number=surah_number,
        verse_scores=verse_scores,
        tartib_score=body.tartib_score,
        takamul_score=body.takamul_score,
        tasmi_score=body.tasmi_score,
        duration_seconds=body.duration_seconds,
    )
    db.commit()
    return QuickVerifyOut(**result)


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
# Audio Revision Playlist
# ══════════════════════════════════════════════════════════════════

@router.get("/revision/audio-playlist", response_model=AudioRevisionPlaylistOut)
def get_audio_revision_playlist(
    student: StudentUser,
    db: DB,
    limit: int = 30,
):
    """
    Build a playlist of verses for passive audio revision.

    Selection logic:
      1. Verses with next_review_date <= today + 2 days (urgent first)
      2. Sorted by SRS tier ascending (FRAGILE > EN_COURS > ACQUIS)
      3. Grouped by surah for coherent listening
      4. Capped at `limit` verses

    Adaptive repetitions per tier:
      - FRAGILE  → 3×
      - EN_COURS → 2×
      - ACQUIS+  → 1×
    """
    from datetime import timedelta
    from ..models.quran import Surah

    today = date.today()
    horizon = today + timedelta(days=2)

    # Fetch due verses
    due_verses = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student.id,
            VerseProgress.next_review_date <= horizon,
            VerseProgress.mastery_score > 0,  # Skip never-practiced verses
        )
        .order_by(
            VerseProgress.mastery_score.asc(),  # Weakest first
            VerseProgress.next_review_date.asc(),
        )
        .limit(limit)
        .all()
    )

    # Build surah name cache
    surah_numbers = list({v.surah_number for v in due_verses})
    surah_map = {}
    if surah_numbers:
        surahs = db.query(Surah).filter(Surah.surah_number.in_(surah_numbers)).all()
        surah_map = {s.surah_number: s.surah_name_ar for s in surahs}

    # Group by surah for coherent listening, then sort within each group
    from collections import defaultdict
    by_surah = defaultdict(list)
    for v in due_verses:
        by_surah[v.surah_number].append(v)

    ordered = []
    for sn in sorted(by_surah.keys(), reverse=True):  # Higher surah numbers first (Juz Amma)
        group = sorted(by_surah[sn], key=lambda v: v.verse_number)
        ordered.extend(group)

    # Build output
    result_verses = []
    total_listens = 0
    for v in ordered:
        tier = tier_from_score(v.mastery_score)
        tier_label = tier.value.lower()

        # Adaptive repeat count
        if tier_label == "fragile":
            repeats = 3
        elif tier_label == "en_cours":
            repeats = 2
        else:
            repeats = 1

        total_listens += repeats
        result_verses.append(RevisionVerseOut(
            surah_number=v.surah_number,
            verse_number=v.verse_number,
            surah_name_ar=surah_map.get(v.surah_number, f"Sourate {v.surah_number}"),
            tier=tier_label,
            mastery_score=v.mastery_score,
            next_review_date=str(v.next_review_date),
        ))

    # Estimate: ~8 seconds per listen on average
    estimated_minutes = max(1, (total_listens * 8) // 60)

    return AudioRevisionPlaylistOut(
        verses=result_verses,
        total_listens=total_listens,
        estimated_minutes=estimated_minutes,
    )


# ══════════════════════════════════════════════════════════════════
# Export router
# ══════════════════════════════════════════════════════════════════
hifz_v2_router = router
